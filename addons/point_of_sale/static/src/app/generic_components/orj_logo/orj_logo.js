import { Component } from "@orj/owl";

export class OrjLogo extends Component {
    static template = "point_of_sale.OrjLogo";
    static props = {
        class: { type: String, optional: true },
        style: { type: String, optional: true },
        monochrome: { type: Boolean, optional: true },
    };
    static defaultProps = {
        class: "",
        style: "",
        monochrome: false,
    };
}
