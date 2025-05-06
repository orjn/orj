/** @orj-module */

import { after, destroy, getFixture } from "@orj/hoot";
import { queryAll } from "@orj/hoot-dom";
import { App, Component, xml } from "@orj/owl";

//-----------------------------------------------------------------------------
// Exports
//-----------------------------------------------------------------------------

/**
 * @param {import("@orj/owl").ComponentConstructor} ComponentClass
 * @param {ConstructorParameters<typeof App>[1]} [config]
 */
export async function mountForTest(ComponentClass, config) {
    if (typeof ComponentClass === "string") {
        ComponentClass = class extends Component {
            static name = "anonymous component";
            static props = {};
            static template = xml`${ComponentClass}`;
        };
    }

    const app = new App(ComponentClass, {
        name: "TEST",
        test: true,
        warnIfNoStaticProps: true,
        ...config,
    });
    const fixture = getFixture();

    after(() => destroy(app));

    fixture.style.backgroundColor = "#fff";
    return app.mount(fixture);
}

/**
 * @param {string} url
 */
export function parseUrl(url) {
    return url.replace(/^.*hoot\/tests/, "@hoot").replace(/(\.test)?\.js$/, "");
}

export function waitForIframes() {
    return Promise.all(
        queryAll("iframe").map(
            (iframe) => new Promise((resolve) => iframe.addEventListener("load", resolve))
        )
    );
}
