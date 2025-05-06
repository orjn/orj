/** @orj-module */

import { Component } from "@orj/owl";

export class ChatterMessageCounter extends Component {
    static template = "project.ChatterMessageCounter";
    static props = {
        count: Number,
    };
}
