/** @orj-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add('stock_notification_wishlist', {
        url: '/shop/wishlist',
    steps: () => [
        {
            content: "Click on 'Be notified when back in stock'",
            trigger: '#wishlist_stock_notification_message',
            run: "click",
        },
        {
            content: "Fill email form",
            trigger: 'div[id="stock_notification_form"] input[name="email"]',
            run: "edit test@test.test",
        },
        {
            content: "Click on the button",
            trigger: '#wishlist_stock_notification_form_submit_button',
            run: "click",
        },
        {
            content: "Success Message",
            trigger: '#stock_notification_success_message',
        },
    ],
});
