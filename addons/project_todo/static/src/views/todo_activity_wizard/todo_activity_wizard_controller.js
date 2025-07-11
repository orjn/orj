/** @orj-module **/

import { onMounted } from "@orj/owl";
import { FormController } from "@web/views/form/form_controller";

export class TodoActivityWizardController extends FormController {
    setup() {
        super.setup();
        onMounted(() => {
            const firstInput = document.querySelector('div.o_field_widget input');
            firstInput.focus();
        });
    }
}
