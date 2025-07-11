import { startWebClient } from "./start";
import { WebClient } from "./webclient/webclient";

/**
 * This file starts the webclient. It is in its own file to allow its replacement
 * in ore. The ore version of the file uses its own webclient import,
 * which is a subclass of the above Webclient.
 */

startWebClient(WebClient);
