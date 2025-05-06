// @orj-module ignore
// ! WARNING: this module must be loaded after `module_loader` but cannot have dependencies !

(function (orj) {
    "use strict";

    if (orj.define.name.endsWith("(hoot)")) {
        return;
    }

    const name = `${orj.define.name} (hoot)`;
    orj.define = {
        [name](name, dependencies, factory) {
            return orj.loader.define(name, dependencies, factory, !name.endsWith(".hoot"));
        },
    }[name];
})(globalThis.orj);
