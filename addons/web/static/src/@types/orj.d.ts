interface OrjModuleErrors {
    cycle?: string | null;
    failed?: Set<string>;
    missing?: Set<string>;
    unloaded?: Set<string>;
}

interface OrjModuleFactory {
    deps: string[];
    fn: OrjModuleFactoryFn;
    ignoreMissingDeps: boolean;
}

class OrjModuleLoader {
    bus: EventTarget;
    checkErrorProm: Promise<void> | null;
    /**
     * Mapping [name => factory]
     */
    factories: Map<string, OrjModuleFactory>;
    /**
     * Names of failed modules
     */
    failed: Set<string>;
    /**
     * Names of modules waiting to be started
     */
    jobs: Set<string>;
    /**
     * Mapping [name => module]
     */
    modules: Map<string, OrjModule>;

    constructor(root?: HTMLElement);

    addJob: (name: string) => void;

    define: (
        name: string,
        deps: string[],
        factory: OrjModuleFactoryFn,
        lazy?: boolean
    ) => OrjModule;

    findErrors: (jobs?: Iterable<string>) => OrjModuleErrors;

    findJob: () => string | null;

    reportErrors: (errors: OrjModuleErrors) => Promise<void>;

    sortFactories: () => void;

    startModule: (name: string) => OrjModule;

    startModules: () => void;
}

type OrjModule = Record<string, any>;

type OrjModuleFactoryFn = (require: (dependency: string) => OrjModule) => OrjModule;

declare const orj: {
    csrf_token: string;
    debug: string;
    define: OrjModuleLoader["define"];
    loader: OrjModuleLoader;
};
