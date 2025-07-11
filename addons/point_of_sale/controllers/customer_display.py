import orj
from orj import http
from orj.http import request
import orj.exceptions


class PosCustomerDisplay(http.Controller):
    @http.route("/pos_customer_display/<id_>/<access_token>", auth="public", type="http", website=True)
    def pos_customer_display(self, id_, access_token, **kw):
        pos_config_sudo = request.env["pos.config"].sudo().browse(int(id_))
        if not orj.tools.consteq(access_token, pos_config_sudo.access_token) or pos_config_sudo.customer_display_type == "none":
            raise orj.exceptions.AccessDenied()
        return request.render(
            "point_of_sale.customer_display_index",
            {
                "session_info": {
                    "user_context": {
                      "lang":  request.env.user.lang or pos_config_sudo.company_id.partner_id.lang
                    },
                    **request.env["ir.http"].get_frontend_session_info(),
                    **pos_config_sudo._get_customer_display_data(),
                },
            },
        )
