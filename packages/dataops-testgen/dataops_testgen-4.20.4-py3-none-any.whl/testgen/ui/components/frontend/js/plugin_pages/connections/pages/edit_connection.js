/**
 * @import { Connection, Flavor } from '../../../components/connection_form.js';
 * 
 * @typedef FormState
 * @type {object}
 * @property {boolean} dirty
 * @property {boolean} valid
 * 
 * @typedef Properties
 * @type {object}
 * @property {Connection} connection
 * @property {Array.<Flavor>} flavors
 */
import van from '../../../van.min.js';
import { Streamlit } from '../../../streamlit.js';
import { Button } from '../../../components/button.js';
import { ConnectionForm } from '../../../components/connection_form.js';
import { emitEvent, getRandomId, getValue, resizeFrameHeightOnDOMChange, resizeFrameHeightToElement } from '../../../utils.js';

const { div } = van.tags;

/**
 * 
 * @param {Properties} props 
 * @returns 
 */
const EditConnection = (props) => {
    Streamlit.setFrameHeight(1);
    window.testgen.isPage = true;

    const domId = `edit-connection-${getRandomId()}`;
    const connection = getValue(props.connection);
    const updatedConnection = van.state(connection);
    const formState = van.state({dirty: false, valid: false});

    resizeFrameHeightToElement(domId);
    resizeFrameHeightOnDOMChange(domId);

    return div(
        { id: domId },
        ConnectionForm(
            {
                connection: props.connection,
                flavors: props.flavors,
                disableFlavor: true,
                onChange: (connection, state) => {
                    formState.val = state;
                    updatedConnection.val = connection;
                },
            },
            () => {
                const formState_ = formState.val;
                const canSave = formState_.dirty && formState_.valid;

                return Button({
                    label: 'Save',
                    color: 'primary',
                    type: 'flat',
                    width: 'auto',
                    disabled: !canSave,
                    onclick: () => emitEvent('SaveConnectionClicked', { payload: updatedConnection.val }),
                });
            },
        )
    );
};

export { EditConnection };
