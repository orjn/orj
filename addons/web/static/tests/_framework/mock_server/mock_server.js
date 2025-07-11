import { before, createJobScopedGetter, expect, getCurrent, registerDebugInfo } from "@orj/hoot";
import { mockFetch, mockWebSocket } from "@orj/hoot-mock";
import { RPCError } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { ensureArray, isIterable } from "@web/core/utils/arrays";
import { isObject } from "@web/core/utils/objects";
import { serverState } from "../mock_server_state.hoot";
import { fetchModelDefinitions, globalCachedFetch, registerModelToFetch } from "../module_set.hoot";
import { DEFAULT_FIELD_VALUES, FIELD_SYMBOL } from "./mock_fields";
import {
    MockServerError,
    getRecordQualifier,
    makeKwArgs,
    makeServerError,
    safeSplit,
} from "./mock_server_utils";

const { DateTime } = luxon;

/**
 * @typedef {{
 *  type: string;
 *  [key: string]: any;
 * }} ActionDefinition
 *
 * @typedef {import("@web/core/domain").DomainListRepr} DomainListRepr
 *
 * @typedef {import("./mock_fields").FieldDefinition} FieldDefinition
 *
 * @typedef {{
 *  actionID?: string | number;
 *  appID?: MenuId;
 *  children?: (MenuId | MenuDefinition)[];
 *  id: MenuId;
 *  name: string;
 *  xmlid?: string;
 * }} MenuDefinition
 *
 * @typedef {number | "root"} MenuId
 *
 * @typedef {MockServerBaseEnvironment & { [modelName: string]: Model }} MockServerEnvironment
 *
 * @typedef {import("./mock_model").Model} Model
 *
 * @typedef {import("./mock_model").ModelConstructor} ModelConstructor
 *
 * @typedef {(params: OrmParams) => any} OrmCallback
 *
 * @typedef {{
 *  args: any[];
 *  kwargs: KwArgs;
 *  method: string;
 *  model: string;
 *  parent: () => any;
 *  request: Request;
 *  route: string;
 * }} OrmParams
 *
 * @typedef {[RegExp, Record<string, string>]} RouteMatcher
 *
 * @typedef {{
 *  final?: boolean;
 *  pure?: boolean;
 * }} RouteOptions
 *
 * @typedef {`/${string}`} RoutePath
 *
 * @typedef {{
 *  actions?: Partial<MockServer["actions"]>;
 *  lang?: string;
 *  lang_parameters?: Partial<MockServer["lang_parameters"]>;
 *  menus?: MenuDefinition[];
 *  models?: Iterable<ModelConstructor>;
 *  modules?: Partial<MockServer["modules"]>;
 *  multi_lang?: import("../mock_server_state.hoot").ServerState["multiLang"];
 *  routes?: Parameters<MockServer["_onRpc"]>;
 *  timezone?: string;
 *  translations?: Record<string, string>;
 * }} ServerParams
 *
 * @typedef {string | Iterable<string> | RegExp} StringMatcher
 *
 * @typedef {(string | RegExp)[]} StringMatchers
 */

/**
 * @template T
 * @typedef {{ mode?: "add" | "replace" = T; }} DefineOptions
 */

/**
 * @template [T={}]
 * @typedef {{
 *  args?: any[];
 *  context?: Record<string, any>;
 *  [key: string]: any;
 * } & Partial<T>} KwArgs
 */

/**
 * @template [T=string]
 * @typedef {(this: MockServer, request: Request, params: Record<T, string>) => any} RouteCallback
 */

//-----------------------------------------------------------------------------
// Internal
//-----------------------------------------------------------------------------

/**
 * @param {import("./mock_model").ModelRecord} user
 */
const authenticateUser = (user) => {
    const { env } = MockServer;
    if (!user?.id) {
        throw new MockServerError("Unauthorized");
    }
    env.cookie.set("sid", user.id);
    env.uid = user.id;
};

/**
 * @template T
 * @param {T} object
 * @return {T}
 */
const deepCopy = (object) => {
    if (!object) {
        return object;
    }
    if (typeof object === "object") {
        if (object?.nodeType) {
            // Nodes
            return object.cloneNode(true);
        } else if (object instanceof Date || object instanceof DateTime) {
            // Dates
            return new object.constructor(object);
        } else if (isIterable(object)) {
            // Iterables
            const copy = [...object].map(deepCopy);
            if (object instanceof Set || object instanceof Map) {
                return new object.constructor(copy);
            } else {
                return copy;
            }
        } else {
            // Other objects
            return Object.fromEntries(
                Object.entries(object).map(([key, object]) => [key, deepCopy(object)])
            );
        }
    }
    return object;
};

/**
 * @param {unknown} error
 */
const ensureError = (error) => (error instanceof Error ? error : new Error(error));

/**
 * @param {DefineOptions<"replace">} [options]
 */
const getAssignAction = (options) => {
    const shouldAdd = options?.mode === "add";
    return function assign(target, key, value) {
        if (shouldAdd && isObject(target[key])) {
            // Add value
            if (Array.isArray(target[key])) {
                target[key].push(...value);
            } else {
                Object.assign(target[key], value);
            }
        } else {
            // Replace value
            target[key] = value;
        }
    };
};

const getCurrentMockServer = () => {
    const { test } = getCurrent();
    if (!test || !test.run) {
        return null;
    }
    if (!mockServers.has(test.run)) {
        mockServers.set(test.run, new MockServer());
    }
    return mockServers.get(test.run);
};

const getCurrentParams = createJobScopedGetter(
    /**
     * @param {ServerParams} previous
     */
    (previous) => ({
        ...previous,
        actions: deepCopy(previous?.actions || []),
        menus: deepCopy(previous?.menus || [DEFAULT_MENU]),
        models: [...(previous?.models || [])], // own instance getters, no need to deep copy
        routes: [...(previous?.routes || [])], // functions, no need to deep copy
    })
);

/**
 * @param {unknown} value
 */
const isNil = (value) => value === null || value === undefined;

/**
 * @param {string} target
 * @param {StringMatchers} matchers
 */
const match = (target, matchers) =>
    matchers.some(
        (matcher) =>
            matcher === "*" ||
            (matcher instanceof RegExp ? matcher.test(target) : target === matcher)
    );

/**
 * @param {string} modelName
 */
const modelNotFoundError = (modelName, consequence) => {
    let message = `cannot find a definition for model "${modelName}"`;
    if (consequence) {
        message += `: ${consequence}`;
    }
    message += ` (did you forget to use \`defineModels()?\`)`;
    return new MockServerError(message);
};

/**
 * @param {Record<string, string> | Iterable<{ id: string, string: string }>} translations
 */
const parseTranslations = (translations) =>
    isIterable(translations)
        ? translations
        : Object.entries(translations).map(([id, string]) => ({ id, string }));

/**
 * @param {unknown} value
 */
const toDisplayName = (value) => {
    const str = String(value)
        .trim()
        .replace(/_id(s)?$/i, "$1")
        .replace(/([a-z])([A-Z])/g, (_, a, b) => `${a} ${b.toLowerCase()}`)
        .replace(/_/g, " ");
    return str[0].toUpperCase() + str.slice(1);
};

class MockServerBaseEnvironment {
    cookie = new Map();

    get companies() {
        return MockServer.env["res.company"].read(serverState.companies.map((c) => c.id));
    }

    get company() {
        return this.companies[0];
    }

    get context() {
        return {
            lang: serverState.lang,
            tz: serverState.timezone,
            uid: serverState.userId,
        };
    }

    get lang() {
        return serverState.lang;
    }

    get uid() {
        return serverState.userId;
    }

    set uid(newUid) {
        serverState.userId = newUid;
        const user = this.user;
        if (user) {
            serverState.partnerId = user.partner_id;
        }
    }

    get user() {
        return MockServer.env["res.users"].browse(serverState.userId)[0];
    }
}

const ACTION_IDENTIFIERS = ["id", "xml_id", "path"];
const ACTION_TYPES = {
    actions: "ir.actions.actions",
    client: "ir.actions.client",
    close: "ir.actions.act_window_close",
    embedded: "ir.embedded.actions",
    report: "ir.actions.report",
    server: "ir.actions.server",
    todo: "ir.actions.todo",
    url: "ir.actions.act_url",
    view: "ir.actions.act_window.view",
    window: "ir.actions.act_window",
};
const ALLOWED_CHARS = {
    default: "[^/]",
    int: "\\d",
    path: ".",
    string: "[\\w:.-]",
};
const DEFAULT_MENU = {
    id: 1,
    appID: 1,
    name: "App1",
};
const ROOT_MENU = {
    id: "root",
    name: "root",
    appID: "root",
};

const R_DATASET_ROUTE = /\/web\/dataset\/call_(button|kw)\/[\w.-]+\/(?<step>\w+)/;
const R_ROUTE_PARAM = /<((?<type>\w+):)?(?<name>[\w-]+)>/g;
const R_WILDCARD = /\*+/g;
const R_WEBCLIENT_ROUTE = /(?<step>\/web\/webclient\/\w+)/;

const mockRpcRegistry = registry.category("mock_rpc");
/** @type {WeakMap<() => any, MockServer>} */
const mockServers = new WeakMap();
const serverFields = new WeakSet();

//-----------------------------------------------------------------------------
// Exports
//-----------------------------------------------------------------------------

export class MockServer {
    /** @type {MockServer | null} */
    static get current() {
        const mockServer = getCurrentMockServer();
        return mockServer?.started ? mockServer : null;
    }

    static get env() {
        return this.current?.env;
    }

    static get state() {
        return serverState;
    }

    // Server params
    lang_parameters = {
        date_format: "%m/%d/%Y",
        decimal_point: ".",
        direction: "ltr",
        grouping: [3, 0],
        time_format: "%H:%M:%S",
        short_time_format: "%H:%M",
        thousands_sep: ",",
        week_start: 7,
    };
    modules = {
        web: { messages: [] },
    };

    // Server env
    env = this._makeServerEnv();

    // Data
    /** @type {ActionDefinition[]} */
    actions = [];
    /** @type {MenuDefinition[]} */
    menus = [];
    /** @type {Record<string, Model>} */
    models = Object.create(null);
    /** @type {Record<string, ModelConstructor>} */
    modelSpecs = Object.create(null);
    /** @type {Set<string>} */
    modelNamesToFetch = new Set();

    // Routes
    /** @type {[StringMatchers, StringMatchers, OrmCallback][]>} */
    ormListeners = [];
    /** @type {[RegExp[], RouteCallback, RouteOptions][]} */
    routes = [];
    started = false;

    // WebSocket connections
    /** @type {import("@orj/hoot-mock").ServerWebSocket[]} */
    websockets = [];

    constructor() {
        // Set default routes
        this._onRoute(["/web/action/load"], this.loadAction);
        this._onRoute(["/web/action/load_breadcrumbs"], this.loadActionBreadcrumbs);
        this._onRoute(["/web/bundle/<string:bundle_name>"], this.loadBundle, { pure: true });
        this._onRoute(["/web/dataset/call_kw", "/web/dataset/call_kw/<path:path>"], this.callKw, {
            final: true,
        });
        this._onRoute(
            ["/web/dataset/call_button", "/web/dataset/call_button/<path:path>"],
            this.callKw,
            { final: true }
        );
        this._onRoute(["/web/dataset/resequence"], this.resequence);
        this._onRoute(["/web/image/<string:model>/<int:id>/<string:field>"], this.loadImage, {
            pure: true,
        });
        this._onRoute(["/web/webclient/load_menus/<string:unique>"], this.loadMenus, {
            pure: true,
        });
        this._onRoute(["/web/webclient/translations/<string:unique>"], this.loadTranslations, {
            pure: true,
        });

        mockFetch((input, init) => this._handle(input, init));
        mockWebSocket((ws) => this.websockets.push(ws));
    }

    /**
     * @param {Partial<ServerParams>} params
     * @param {DefineOptions<"replace">} [options]
     */
    configure(params, options) {
        const assign = getAssignAction(options);
        if (params.actions) {
            assign(this, "actions", params.actions);
        }
        if (params.lang) {
            assign(serverState, "lang", params.lang);
        }
        if (params.lang_parameters) {
            // Never fully replace "lang_parameters"
            Object.assign(this.lang_parameters, params.lang_parameters);
        }
        if (params.menus) {
            assign(this, "menus", params.menus);
        }
        if (params.models) {
            for (const ModelClass of params.models) {
                const model = this._getModelDefinition(ModelClass);
                assign(this.modelSpecs, model._name, model);
            }
            if (this.started) {
                this._loadModels();
            }
        }
        if (params.modules) {
            for (const [module, values] in Object.entries(params.modules)) {
                this.modules[module] ||= { messages: [] };
                assign(
                    this.modules[module],
                    "messages",
                    parseTranslations(values.message || values)
                );
            }
        }
        if (params.multi_lang) {
            assign(serverState, "multiLang", params.multi_lang);
        }
        if (params.timezone) {
            assign(serverState, "timezone", params.timezone);
        }
        if (params.translations) {
            assign(this.modules.web, "messages", parseTranslations(params.translations));
        }
        if (params.routes) {
            for (const args of params.routes) {
                this._onRpc(...args);
            }
        }

        return this;
    }

    /**
     * @param {string} [url]
     */
    getWebSockets(url) {
        return url ? this.websockets.filter((ws) => ws.url.includes(url)) : this.websockets;
    }

    async start() {
        if (this.started) {
            throw new MockServerError("MockServer has already been started");
        }
        this.started = true;

        await this._loadModels();
        this._generateRecords();

        return this;
    }

    //-------------------------------------------------------------------------
    // Private methods
    //-------------------------------------------------------------------------

    /**
     * @private
     * @param {OrmParams} params
     */
    _callOrm(params) {
        const { method, model: modelName } = params;
        const args = params.args || [];
        const kwargs = makeKwArgs(params.kwargs || {});

        // Try to find a model method
        if (modelName) {
            const model = this.env[modelName];
            if (typeof model[method] === "function") {
                const expectedLength = model[method].length;
                while (args.length < expectedLength) {
                    args.push(undefined);
                }
                return model[method](...args, kwargs);
            }

            // Try to find a parent model method
            for (const parentName of safeSplit(model._inherit)) {
                const parentModel = this.env[parentName];
                if (typeof parentModel[method] === "function") {
                    const expectedLength = parentModel[method].length;
                    while (args.length < expectedLength) {
                        args.push(undefined);
                    }
                    return parentModel[method].call(model, ...args, kwargs);
                }
            }
        }

        throw new MockServerError(`unimplemented ORM method: ${modelName}.${method}`);
    }

    /**
     * @private
     * @param {string | number | false} id
     */
    _findAction(id) {
        const strId = String(id);
        const actions = this.actions.filter((action) => {
            for (const identifier of ACTION_IDENTIFIERS) {
                if (String(action[identifier]) === strId) {
                    return action;
                }
            }
        });
        if (!actions.length) {
            throw makeServerError({
                errorName: "orj.addons.web.controllers.action.MissingActionError",
                message: `The action ${JSON.stringify(id)} does not exist`,
            });
        }
        return this._getAction(Object.assign({}, ...actions));
    }

    /**
     * @private
     * @param {OrmParams} params
     */
    _findOrmListeners({ method, model }) {
        const callbacks = [this._callOrm];
        for (const [modelMatchers, methodMatchers, callback] of this.ormListeners) {
            if (match(model, modelMatchers) && match(method, methodMatchers)) {
                callbacks.unshift(callback);
            }
        }
        return callbacks;
    }

    /**
     * @private
     * @param {string} route
     */
    _findRouteListeners(route) {
        /** @type {[RouteCallback, Record<string, string>, RouteOptions][]} */
        const listeners = [];
        for (const [routeRegexes, callback, options] of this.routes) {
            for (const regex of routeRegexes) {
                const argsMatch = route.match(regex);
                if (argsMatch) {
                    listeners.unshift([callback, argsMatch.groups, options]);
                }
            }
        }
        return listeners;
    }

    /**
     * @private
     */
    _generateRecords() {
        for (const model of Object.values(this.models)) {
            const seenIds = new Set();
            for (const record of model) {
                // Check for unknown fields
                for (const fieldName in record) {
                    if (!(fieldName in model._fields)) {
                        throw new MockServerError(
                            `unknown field "${fieldName}" on ${getRecordQualifier(
                                record
                            )} in model "${model._name}"`
                        );
                    }
                }
                // Apply values and default values
                for (const [fieldName, fieldDef] of Object.entries(model._fields)) {
                    if (fieldName === "id") {
                        record[fieldName] ||= model._getNextId();
                        continue;
                    }
                    if ("default" in fieldDef) {
                        const def = fieldDef.default;
                        record[fieldName] ??=
                            typeof def === "function" ? def.call(this, record) : def;
                    }
                    record[fieldName] ??= DEFAULT_FIELD_VALUES[fieldDef.type]?.() ?? false;
                }
                if (seenIds.has(record.id)) {
                    throw new MockServerError(
                        `duplicate ID ${record.id} in model "${model._name}"`
                    );
                }
                seenIds.add(record.id);
            }
        }

        // creation of the ir.model.fields records, required for tracked fields
        const IrModelFields = this.models["ir.model.fields"];
        if (IrModelFields) {
            for (const model of Object.values(this.models)) {
                for (const [fieldName, field] of Object.entries(model._fields)) {
                    if (field.tracking) {
                        IrModelFields.create({
                            model: model._name,
                            name: fieldName,
                            ttype: field.type,
                        });
                    }
                }
            }
        }

        Object.values(this.models).forEach((model) => model._applyComputesAndValidate());
    }

    /**
     * @private
     * @param {Partial<ActionDefinition>} rawAction
     */
    _getAction(rawAction) {
        const mainIdentifier = ACTION_IDENTIFIERS.find((identifier) => rawAction[identifier]);
        const id = rawAction[mainIdentifier];
        const action = {
            binding_type: "action",
            binding_view_types: "list,form",
            id,
            type: ACTION_TYPES.window,
            xml_id: id,
            ...rawAction,
        };
        switch (action.type) {
            case ACTION_TYPES.client: {
                action.context ||= {};
                action.target ??= "current";
                break;
            }
            case ACTION_TYPES.embedded: {
                // Embedded actions are treated as regular actions for simplicity's sake
                action.context ||= {};
                action.domain ||= [];
                action.filter_ids ||= [];
                action.groups_id ||= [];
                break;
            }
            case ACTION_TYPES.report: {
                action.binding_type = rawAction.binding_type ?? "report";
                action.report_type ??= "qweb-pdf";
                action.groups_id ||= [];
                break;
            }
            case ACTION_TYPES.server: {
                action.available_model_ids ||= [];
                action.child_ids ||= [];
                action.code ??= "";
                action.evaluation_type ??= "value";
                action.groups_id ||= [];
                action.sequence ??= 5;
                action.state ??= "object_write";
                action.update_boolean_value ??= "true";
                action.update_m2m_operation ??= "add";
                action.usage ??= "ir_actions_server";
                action.webhook_field_ids ||= [];
                break;
            }
            case ACTION_TYPES.todo: {
                action.sequence ??= 10;
                action.state ??= "open";
                break;
            }
            case ACTION_TYPES.url: {
                action.target ??= "new";
                break;
            }
            case ACTION_TYPES.window: {
                action.context ||= {};
                action.embedded_action_ids ||= [];
                action.group_ids ||= [];
                action.limit ??= 80;
                action.mobile_view_mode ??= "kanban";
                action.target ??= "current";
                action.view_ids ||= [];
                action.view_mode ??= "list,form";
                for (const embeddedAction of this.actions) {
                    if (
                        embeddedAction.type === ACTION_TYPES.embedded &&
                        embeddedAction.parent_action_id === id
                    ) {
                        action.embedded_action_ids.push(this._getAction(embeddedAction));
                    }
                }
                break;
            }
            default: {
                if (!(action.type in ACTION_TYPES)) {
                    throw new MockServerError(
                        `invalid action type "${action.type}" in action ${id}`
                    );
                }
            }
        }
        return action;
    }

    /**
     * @private
     * @param {ModelConstructor} ModelClass
     * @returns {Model}
     */
    _getModelDefinition(ModelClass) {
        const model = ModelClass.definition;

        // Server model
        if (model._fetch) {
            this.modelNamesToFetch.add(model._name);
        }

        // Model fields
        for (const [fieldName, fieldDescriptor] of Object.entries(ModelClass._fields)) {
            if (!(FIELD_SYMBOL in fieldDescriptor)) {
                continue;
            }

            if (fieldDescriptor.name) {
                throw new MockServerError(
                    `cannot set the name of field "${fieldName}" from its definition: got "${fieldDescriptor.name}"`
                );
            }
            fieldDescriptor.string ||= toDisplayName(fieldName);

            /** @type {FieldDefinition} */
            const fieldDef = { ...fieldDescriptor, name: fieldName };

            // On change function
            const onChange = fieldDef.onChange;
            if (typeof onChange === "function") {
                model._onChanges[fieldName] = onChange.bind(model);
            }

            model._fields[fieldName] = fieldDef;
        }

        return model;
    }

    /**
     * @private
     * @param {string} url
     * @param {RequestInit} init
     * @param {RouteOptions} [options]
     */
    async _handle(url, init, options = {}) {
        if (!this.started) {
            throw new MockServerError(
                `cannot handle \`fetch\`: server has not been started (did you forget to call \`start()\`?)`
            );
        }

        const method = init?.method?.toUpperCase() || (init?.body ? "POST" : "GET");
        const request = new Request(url, { method, ...(init || {}) });

        const route = new URL(request.url).pathname;
        const listeners = this._findRouteListeners(route);
        if (!listeners.length) {
            throw new MockServerError(`unimplemented server route: ${route}`);
        }

        let result = null;
        for (const [callback, routeParams, routeOptions] of listeners) {
            const pure = options.pure ?? routeOptions.pure;
            const final = options.final ?? routeOptions.final;
            try {
                result = await callback.call(this, request, routeParams);
            } catch (error) {
                if (pure) {
                    throw error;
                }
                result = ensureError(error);
            }
            if (!isNil(result) || final) {
                if (pure) {
                    return result;
                }
                if (result instanceof RPCError) {
                    return { error: result, result: null };
                }
                if (result instanceof Error) {
                    return {
                        error: {
                            code: 418,
                            data: result,
                            message: result.message,
                            type: result.name,
                        },
                        result: null,
                    };
                }
                return { error: null, result };
            }
        }

        // There was a matching controller that wasn't call_kw but it didn't return anything: treat it as JSON
        return { error: null, result };
    }

    /**
     * @private
     */
    async _loadModels() {
        const models = Object.values(this.modelSpecs);
        const serverModelInheritances = new Set();
        this.modelSpecs = Object.create(null);
        if (this.modelNamesToFetch.size) {
            const modelEntries = await fetchModelDefinitions(this.modelNamesToFetch);
            this.modelNamesToFetch.clear();

            for (const [
                name,
                { description, fields, inherit, order, parent_name, rec_name, ...others },
            ] of modelEntries) {
                const localModelDef = models.find((model) => model._name === name);
                localModelDef._description = description;
                localModelDef._order = order;
                localModelDef._parent_name = parent_name;
                localModelDef._rec_name = rec_name;
                const inheritList = new Set(safeSplit(localModelDef._inherit));
                for (const inherittedModelName of inherit) {
                    inheritList.add(inherittedModelName);
                    serverModelInheritances.add([name, inherittedModelName].join(","));
                }
                localModelDef._inherit = [...inheritList].join(",");
                for (const name in others) {
                    localModelDef[name] = others[name];
                }
                for (const [fieldName, serverFieldDef] of Object.entries(fields)) {
                    const serverField = {
                        ...serverFieldDef,
                        ...localModelDef._fields[fieldName],
                    };
                    serverFields.add(serverField);
                    localModelDef._fields[fieldName] = serverField;
                }
            }
        }

        // Register models on mock server instance
        for (const model of models) {
            // Validate _rec_name
            if (model._rec_name) {
                if (!(model._rec_name in model._fields)) {
                    throw new MockServerError(
                        `invalid _rec_name "${model._rec_name}" on model "${model._name}": field does not exist`
                    );
                }
            } else if ("name" in model._fields) {
                model._rec_name = "name";
            } else if ("x_name" in model._fields) {
                model._rec_name = "x_name";
            }

            if (model._name in this.env) {
                throw new MockServerError(
                    `cannot register model "${model._name}": a model or a server environment property with the same name already exists`
                );
            }

            this.models[model._name] = model;
        }

        // Inheritance
        for (const model of models) {
            // Apply inherited fields
            for (const modelName of safeSplit(model._inherit)) {
                if (!modelName) {
                    continue;
                }
                const parentModel = this.models[modelName];
                if (parentModel) {
                    for (const fieldName in parentModel._fields) {
                        model._fields[fieldName] ??= parentModel._fields[fieldName];
                    }
                } else if (serverModelInheritances.has([model._name, modelName].join(","))) {
                    // Inheritance comes from the server, so we can safely remove it:
                    // it means that the inherited model has not been fetched in this
                    // context.
                    model._inherit = model._inherit.replace(new RegExp(`${modelName},?`), "");
                } else {
                    throw modelNotFoundError(modelName, "could not inherit from model");
                }
            }

            // Check missing models
            for (const field of Object.values(model._fields)) {
                if (field.relation && !this.models[field.relation]) {
                    if (serverFields.has(field)) {
                        delete model._fields[field.name];
                    } else {
                        throw modelNotFoundError(field.relation, "could not find model");
                    }
                }
            }
        }

        // Computed & related fields
        for (const model of models) {
            for (const { compute, name, related } of Object.values(model._fields)) {
                if (compute) {
                    // Computed field
                    /** @type {(this: Model, fieldName: string) => void} */
                    let computeFn = compute;
                    if (typeof computeFn !== "function") {
                        computeFn = model[computeFn];
                        if (typeof computeFn !== "function") {
                            throw new MockServerError(
                                `could not find compute function "${computeFn}" on model "${model._name}"`
                            );
                        }
                    }

                    model._computes[name] = computeFn;
                } else if (related) {
                    // Related field
                    model._related.add(name);
                }
            }
        }
    }

    /**
     * @private
     * @returns {MockServerEnvironment}
     */
    _makeServerEnv() {
        const serverEnv = new MockServerBaseEnvironment();
        return new Proxy(serverEnv, {
            get: (target, p) => {
                if (p in target || typeof p !== "string" || p === "then") {
                    return Reflect.get(target, p);
                }
                const model = Reflect.get(this.models, p);
                if (!model) {
                    throw modelNotFoundError(p, "could not get model from server environment");
                }
                return model;
            },
            has: (target, p) => Reflect.has(target, p) || Reflect.has(this.models, p),
        });
    }

    /**
     * @overload
     * @param {OrmCallback} callback
     */
    /**
     * @overload
     * @param {StringMatchers} method
     * @param {OrmCallback} callback
     */
    /**
     * @overload
     * @param {StringMatchers} model
     * @param {StringMatcher} method
     * @param {OrmCallback} callback
     */
    /**
     * @private
     * @param {StringMatchers | OrmCallback} model
     * @param {StringMatcher | OrmCallback} [method]
     * @param {OrmCallback} [callback]
     */
    _onOrmMethod(...args) {
        /** @type {OrmCallback[]} */
        const [callback] = ensureArray(args.pop());
        /** @type {StringMatchers} */
        const method = ensureArray(args.pop() || "*");
        /** @type {StringMatchers} */
        const model = ensureArray(args.pop() || "*");

        if (typeof callback !== "function") {
            throw new Error(`onRpc: expected callback to be a function, got: ${callback}`);
        }

        this.ormListeners.push([model, method, callback]);
    }

    /**
     * @private
     * @param {RoutePath[]} routes
     * @param {RouteCallback} callback
     * @param {RouteOptions} options
     */
    _onRoute(routes, callback, options) {
        const routeRegexes = routes.map((route) => {
            const regexString = route
                // Replace parameters by regex notation and store their names
                .replaceAll(R_ROUTE_PARAM, (...args) => {
                    const { name, type } = args.pop();
                    return `(?<${name}>${ALLOWED_CHARS[type] || ALLOWED_CHARS.default}+)`;
                })
                // Replace glob wildcards by regex wildcard
                .replaceAll(R_WILDCARD, ".*");
            return new RegExp(`^${regexString}$`, "i");
        });

        this.routes.push([routeRegexes, callback, options || {}]);
    }

    /**
     * @overload
     * @param {OrmCallback} callback
     */
    /**
     * @overload
     * @param {RoutePath | Iterable<RoutePath>} route
     * @param {RouteCallback} callback
     * @param {RouteOptions} [options]
     */
    /**
     * @overload
     * @param {StringMatcher} method
     * @param {OrmCallback} callback
     */
    /**
     * @overload
     * @param {StringMatcher} model
     * @param {StringMatcher} method
     * @param {OrmCallback} callback
     */
    /**
     * @private
     * @param {StringMatcher | OrmCallback} route
     * @param {RouteCallback | StringMatcher | OrmCallback} [callback]
     * @param {RouteOptions | OrmCallback} [options]
     */
    _onRpc(...args) {
        const ormArgs = [];
        const routeArgs = [];
        for (const val of ensureArray(args.shift())) {
            if (typeof val === "string" && val.startsWith("/")) {
                routeArgs.push(val);
            } else {
                ormArgs.push(val);
            }
        }
        if (ormArgs.length) {
            this._onOrmMethod(ormArgs, ...args);
        }
        if (routeArgs.length) {
            this._onRoute(routeArgs, ...args);
        }
        return this;
    }

    //-------------------------------------------------------------------------
    // Route methods
    //-------------------------------------------------------------------------

    /**
     * @type {RouteCallback}
     */
    async callKw(request) {
        const callNextOrmCallback = () => {
            const nextCallback = ormListeners.shift();
            return nextCallback.call(this, callbackParams);
        };

        const { params } = await request.json();
        const callbackParams = {
            parent: callNextOrmCallback,
            request,
            route: new URL(request.url).pathname,
            ...params,
        };
        const ormListeners = this._findOrmListeners(params);
        while (ormListeners.length) {
            const result = await callNextOrmCallback();
            if (!isNil(result)) {
                return result;
            }
        }
        return null;
    }

    /**
     * @type {RouteCallback}
     */
    async loadAction(request) {
        const { params } = await request.json();
        return this._findAction(params.action_id);
    }

    /**
     * @type {RouteCallback}
     */
    async loadActionBreadcrumbs(request) {
        const { params } = await request.json();
        const { actions } = params;
        return actions.map(({ action: actionId, model, resId }) => {
            /** @type {string} */
            let displayName;
            if (actionId) {
                const action = this._findAction(actionId);
                if (resId) {
                    displayName = this.env[action.res_model].browse(resId)[0].display_name;
                } else {
                    displayName = action.name;
                }
            } else if (model) {
                if (!resId) {
                    throw new Error("Actions with a 'model' should also have a 'resId'");
                }
                displayName = this.env[model].browse(resId)[0].display_name;
            } else {
                throw new Error("Actions should have either an 'action' (ID or path) or a 'model'");
            }
            return { display_name: displayName };
        });
    }

    /**
     * @type {RouteCallback<"bundle_name">}
     */
    async loadBundle(request) {
        // No mock here: we want to fetch the actual bundle (and cache it between suites),
        // although there is a protection to ensure a bundle doesn't leak to the
        // next test.
        const initiatorTestId = getCurrent().test?.id;
        if (initiatorTestId) {
            const result = await globalCachedFetch(request.url);
            if (initiatorTestId === getCurrent().test?.id) {
                return result;
            }
        }
        return new Promise(() => {});
    }

    /**
     * @type {RouteCallback<"model" | "field" | "id">}
     */
    async loadImage(request, { id, model, field }) {
        return `<fake url to record ${id} on ${model}.${field}>`;
    }

    /**
     * @type {RouteCallback<"unique">}
     */
    async loadMenus() {
        /** @type {MenuId[]} */
        const allChildIds = new Set();
        /** @type {Record<MenuId, MenuDefinition>} */
        const menuDict = {};
        /** @type {MenuDefinition[]} */
        const menuStack = [{ ...ROOT_MENU, children: this.menus }];
        while (menuStack.length) {
            const menu = menuStack.shift();
            /** @type {Set<MenuId>} */
            const childIds = new Set();
            menuDict[menu.id] = { ...menuDict[menu.id], ...menu };
            for (const childMenuOrId of menuDict[menu.id].children) {
                let childId = childMenuOrId;
                if (isObject(childMenuOrId)) {
                    childId = childMenuOrId.id;
                    menuStack.push({
                        appID: childId,
                        children: [],
                        name: `App${childId}`,
                        ...childMenuOrId,
                    });
                }
                allChildIds.add(childId);
                childIds.add(childId);
            }
            menuDict[menu.id].children = [...childIds].sort((a, b) => a - b);
        }
        const missingMenuIds = [...allChildIds].filter((id) => !(id in menuDict));
        if (missingMenuIds.length) {
            throw new MockServerError(`missing menu ID(s): ${missingMenuIds.join(", ")}`);
        }
        return menuDict;
    }

    /**
     * @type {RouteCallback<"unique">}
     */
    async loadTranslations() {
        const langParameters = { ...this.lang_parameters };
        if (typeof langParameters.grouping !== "string") {
            langParameters.grouping = JSON.stringify(langParameters.grouping);
        }
        return {
            lang: serverState.lang,
            lang_parameters: langParameters,
            modules: this.modules,
            multi_lang: serverState.multiLang,
        };
    }

    /**
     * @type {RouteCallback}
     */
    async resequence(request) {
        const { params } = await request.json();
        const offset = params.offset ? Number(params.offset) : 0;
        const field = params.field || "sequence";
        if (!(field in this.env[params.model]._fields)) {
            return false;
        }
        for (const index in params.ids) {
            const record = this.env[params.model].find((r) => r.id === params.ids[index]);
            record[field] = Number(index) + offset;
        }
        return true;
    }
}

/**
 * Authenticates a user on the mock server given its login and password.
 *
 * @param {string} login
 * @param {string} password
 */
export function authenticate(login, password) {
    const { env } = MockServer;
    const [user] = env["res.users"]._filter(
        [
            ["login", "=", login],
            ["password", "=", password],
        ],
        { active_test: false }
    );
    authenticateUser(user);
    env.cookie.set("authenticated_user_sid", env.cookie.get("sid"));
}

/**
 * @param {ActionDefinition[]} actions
 * @param {DefineOptions<"add">} [options]
 */
export function defineActions(actions, options) {
    return defineParams({ actions }, { mode: "add", ...options }).actions;
}

/**
 * @param {MenuDefinition[]} menus
 * @param {DefineOptions<"add">} [options]
 */
export function defineMenus(menus, options) {
    return defineParams({ menus }, { mode: "add", ...options }).menus;
}

/**
 * Registers a list of model classes on the current/future {@link MockServer} instance.
 *
 * @param  {ModelConstructor[] | Record<string, ModelConstructor>} ModelClasses
 * @param {DefineOptions<"add">} [options]
 */
export function defineModels(ModelClasses, options) {
    const models = Object.values(ModelClasses);
    for (const ModelClass of models) {
        const instance = new ModelClass();
        // we cannot get the `definition` as this will trigger the model creation
        if (instance._fetch) {
            registerModelToFetch(instance._name);
        }
    }

    return defineParams({ models }, { mode: "add", ...options }).models;
}

/**
 * @param {ServerParams} params
 * @param {DefineOptions<"replace">} [options]
 */
export function defineParams(params, options) {
    const assign = getAssignAction(options);
    before(() => {
        const currentParams = getCurrentParams();
        for (const [key, value] of Object.entries(params)) {
            assign(currentParams, key, value);
        }

        MockServer.current?.configure(params);
    });

    return params;
}

/**
 * Logs out the current user (if any)
 */
export function logout() {
    const { env } = MockServer;
    if (env.cookie.get("authenticated_user_sid") === env.cookie.get("sid")) {
        env.cookie.delete("authenticated_user_sid");
    }
    env.cookie.delete("sid");
    const [publicUser] = env["res.users"].browse(serverState.publicUserId, {
        active_test: false,
    });
    authenticate(publicUser.login, publicUser.password);
}

/**
 * Shortcut function to create and start a {@link MockServer}.
 */
export async function makeMockServer() {
    const mockServer = getCurrentMockServer();

    // Add routes from "mock_rpc" registry
    for (const [route, callback] of mockRpcRegistry.getEntries()) {
        if (typeof callback === "function") {
            mockServer._onRpc(route, callback);
        }
    }

    // Add other ambiant params
    mockServer.configure(getCurrentParams());

    registerDebugInfo("mock server", mockServer);

    return mockServer.start();
}

/**
 * @overload
 * @param {OrmCallback} callback
 */
/**
 * @overload
 * @param {RoutePath | Iterable<RoutePath>} route
 * @param {RouteCallback} callback
 * @param {RouteOptions} [options]
 */
/**
 * @overload
 * @param {StringMatcher} method
 * @param {OrmCallback} callback
 */
/**
 * @overload
 * @param {StringMatcher} model
 * @param {StringMatcher} method
 * @param {OrmCallback} callback
 */
/**
 * Registers an RPC handler on the current/future {@link MockServer} instance.
 *
 * @type {MockServer["_onRpc"]}
 */
export function onRpc(...args) {
    return defineParams({ routes: [args] }, { mode: "add" }).routes;
}

/**
 * calls expect.step for all network calls. Because of how the mock server
 * works, you need to call this *after* all your custom mockRPCs that return
 * something, otherwise the mock server will not call this function's handler.
 *
 * @returns {void}
 */
export function stepAllNetworkCalls() {
    onRpc("/*", (request) => {
        const route = new URL(request.url).pathname;
        let match = route.match(R_DATASET_ROUTE);
        if (match) {
            return void expect.step(match.groups?.step || route);
        }
        match = route.match(R_WEBCLIENT_ROUTE);
        if (match) {
            return void expect.step(match.groups?.step || route);
        }
        return void expect.step(route);
    });
}

/**
 * Executes the given callback as the given user, then restores the previous user.
 *
 * @param {number} userId
 * @param {() => any} fn
 */
export async function withUser(userId, fn) {
    const { env } = MockServer;
    const currentUser = env.user;
    const [targetUser] = env["res.users"].browse(userId, { active_test: false });
    authenticateUser(targetUser);
    let result;
    try {
        result = await fn();
    } finally {
        if (currentUser) {
            authenticateUser(currentUser);
        } else {
            logout();
        }
    }
    return result;
}
