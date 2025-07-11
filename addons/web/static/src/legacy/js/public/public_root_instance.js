/** @orj-module alias=root.widget */
import { PublicRoot, createPublicRoot } from "./public_root";
import lazyloader from "@web/legacy/js/public/lazyloader";

const prom = createPublicRoot(PublicRoot);
lazyloader.registerPageReadinessDelay(prom);
export default prom;
