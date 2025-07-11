import { after, afterEach, beforeEach, registerDebugInfo } from "@orj/hoot";
import { startRouter } from "@web/core/browser/router";
import { createDebugContext } from "@web/core/debug/debug_context";
import { translatedTerms, translationLoaded } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { pick } from "@web/core/utils/objects";
import { patch } from "@web/core/utils/patch";
import { makeEnv, startServices } from "@web/env";
import { MockServer, makeMockServer } from "./mock_server/mock_server";

/**
 * @typedef {Record<keyof Services, any>} Dependencies
 *
 * @typedef {import("@web/env").OrjEnv} OrjEnv
 *
 * @typedef {import("@web/core/registry").Registry} Registry
 *
 * @typedef {import("services").ServiceFactories} Services
 */

//-----------------------------------------------------------------------------
// Internals
//-----------------------------------------------------------------------------

/**
 * TODO: remove when services do not have side effects anymore
 * This forsaken block of code ensures that all are properly cleaned up after each
 * test because they were populated during the starting process of some services.
 *
 * @param {Registry} registry
 */
const registerRegistryForCleanup = (registry) => {
    const content = Object.entries(registry.content).map(([key, value]) => [key, value.slice()]);
    registriesContent.set(registry, content);

    for (const subRegistry of Object.values(registry.subRegistries)) {
        registerRegistryForCleanup(subRegistry);
    }
};

const registriesContent = new WeakMap();
/** @type {OrjEnv | null} */
let currentEnv = null;

// Registers all registries for cleanup in all tests
beforeEach(() => registerRegistryForCleanup(registry));
afterEach(() => restoreRegistry(registry));

//-----------------------------------------------------------------------------
// Exports
//-----------------------------------------------------------------------------

/**
 * Empties the given registry.
 *
 * @param {Registry} registry
 */
export function clearRegistry(registry) {
    registry.content = {};
    registry.elements = null;
    registry.entries = null;
}

export function getMockEnv() {
    return currentEnv;
}

/**
 * @template {keyof Services} T
 * @param {T} name
 * @returns {Services[T]}
 */
export function getService(name) {
    return currentEnv.services[name];
}

/**
 * Makes a mock environment along with a mock server
 *
 * @param {Partial<OrjEnv>} [partialEnv]
 */
export async function makeMockEnv(partialEnv, { makeNew = false } = {}) {
    if (currentEnv && !makeNew) {
        throw new Error(
            `cannot create mock environment: a mock environment has already been declared`
        );
    }

    if (!MockServer.current) {
        await makeMockServer();
    }

    currentEnv = makeEnv();
    after(() => {
        currentEnv = null;

        // Ideally: should be done in a patch of the localization service, but this
        // is less intrusive for now.
        if (translatedTerms[translationLoaded]) {
            for (const key in translatedTerms) {
                delete translatedTerms[key];
            }
            translatedTerms[translationLoaded] = false;
        }
    });
    Object.assign(currentEnv, partialEnv, createDebugContext(currentEnv)); // This is needed if the views are in debug mode

    registerDebugInfo("env", currentEnv);

    startRouter();
    await startServices(currentEnv);

    return currentEnv;
}

/**
 * Makes a mock environment for dialog tests
 *
 * @param {Partial<OrjEnv>} [partialEnv]
 * @returns {Promise<OrjEnv>}
 */
export async function makeDialogMockEnv(partialEnv) {
    return makeMockEnv({
        ...partialEnv,
        dialogData: {
            close: () => {},
            isActive: true,
            scrollToOrigin: () => {},
            ...partialEnv?.dialogData,
        },
    });
}

/**
 * @template {keyof Services} T
 * @param {T} name
 * @param {Partial<Services[T]> |
 *  (env: OrjEnv, dependencies: Dependencies) => Services[T]
 * } serviceFactory
 */
export function mockService(name, serviceFactory) {
    const serviceRegistry = registry.category("services");
    const originalService = serviceRegistry.get(name, null);
    serviceRegistry.add(
        name,
        {
            ...originalService,
            start(env, dependencies) {
                if (typeof serviceFactory === "function") {
                    return serviceFactory(env, dependencies);
                } else {
                    const service = originalService.start(env, dependencies);
                    if (service instanceof Promise) {
                        service.then((value) => patch(value, serviceFactory));
                    } else {
                        patch(service, serviceFactory);
                    }
                    return service;
                }
            },
        },
        { force: true }
    );

    // Patch already initialized service
    if (currentEnv?.services?.[name]) {
        if (typeof serviceFactory === "function") {
            const dependencies = pick(currentEnv.services, ...(originalService.dependencies || []));
            currentEnv.services[name] = serviceFactory(currentEnv, dependencies);
        } else {
            patch(currentEnv.services[name], serviceFactory);
        }
    }
}

/**
 * @param {Registry} registry
 */
export function restoreRegistry(registry) {
    if (registriesContent.has(registry)) {
        clearRegistry(registry);

        registry.content = Object.fromEntries(registriesContent.get(registry));
    }

    for (const subRegistry of Object.values(registry.subRegistries)) {
        restoreRegistry(subRegistry);
    }
}
