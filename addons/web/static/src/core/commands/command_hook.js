import { useService } from "@web/core/utils/hooks";

import { useEffect } from "@orj/owl";

/**
 * @typedef {import("./command_service").CommandOptions} CommandOptions
 */

/**
 * This hook will subscribe/unsubscribe the given subscription
 * when the caller component will mount/unmount.
 *
 * @param {string} name
 * @param {()=>(void | import("@web/core/commands/command_palette").CommandPaletteConfig)} action
 * @param {CommandOptions} [options]
 */
export function useCommand(name, action, options = {}) {
    const commandService = useService("command");
    useEffect(
        () => commandService.add(name, action, options),
        () => []
    );
}
