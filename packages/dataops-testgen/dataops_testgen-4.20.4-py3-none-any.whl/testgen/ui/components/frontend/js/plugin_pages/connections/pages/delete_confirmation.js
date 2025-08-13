/**
 * @import { Connection } from '../../../components/connection_form.js';
 *
 * @typedef Result
 * @type {object}
 * @property {boolean} success
 * @property {string} message
 *
 * @typedef Properties
 * @type {object}
 * @property {string} project_code
 * @property {Connection} connection
 * @property {boolean} can_be_deleted
 * @property {Result?} result
 */

import van from '../../../van.min.js';
import { Streamlit } from '../../../streamlit.js';
import { emitEvent, getValue, loadStylesheet, resizeFrameHeightOnDOMChange, resizeFrameHeightToElement } from '../../../utils.js';
import { Button } from '../../../components/button.js';
import { Toggle } from '../../../components/toggle.js';
import { Attribute } from '../../../components/attribute.js';
import { Alert } from '../../../components/alert.js';

const { div, h3, hr, span, b } = van.tags;

/**
 * @param {Properties} props
 * @returns
 */
const ConnectionDeleteConfirmation = (props) => {
    loadStylesheet('connection-delete-confirmation', stylesheet);
    Streamlit.setFrameHeight(1);
    window.testgen.isPage = true;

    const wrapperId = 'connections-delete-wrapper';
    const connection = getValue(props.connection);
    const confirmDeleteRelated = van.state(false);
    const deleteDisabled = van.derive(() => !getValue(props.can_be_deleted) && !confirmDeleteRelated.val);

    resizeFrameHeightToElement(wrapperId);
    resizeFrameHeightOnDOMChange(wrapperId);

    return div(
        { id: wrapperId, class: 'flex-column' },
        div(
            { class: 'flex-column fx-gap-4' },
            span(
                'Are you sure you want to delete the connection ',
                b(connection.connection_name),
                '?',
            ),
            Attribute({
                label: 'Database Type',
                value: connection.sql_flavor,
            }),
            Attribute({
                label: 'Host',
                value: connection.project_host,
            }),
            connection.connect_by_url
                ? Attribute({
                    label: 'URL',
                    value: connection.url,
                })
                : Attribute({
                    label: 'Database',
                    value: connection.project_db,
                }),
        ),
        () => !getValue(props.can_be_deleted)
            ? div(
                { class: 'flex-column fx-gap-4 mt-4' },
                Alert(
                    { type: 'warn' },
                    div('This Connection has related data, which may include profiling, test definitions, and test results.'),
                    div({ class: 'mt-2' }, 'If you proceed, all related data will be permanently deleted.'),
                ),
                Toggle({
                    name: 'confirm-delete-connection',
                    label: span(
                        'Yes, delete the connection ',
                        b(connection.connection_name),
                        ' and related TestGen data.',
                    ),
                    checked: confirmDeleteRelated,
                    onChange: (value) => confirmDeleteRelated.val = value,
                }),
            )
            : '',

        div(
            { class: 'flex-row fx-justify-content-flex-end' },
            Button({
                type: () => deleteDisabled.val ? 'stroked' : 'flat',
                color: () => deleteDisabled.val ? 'basic' : 'warn',
                label: 'Delete',
                style: 'width: auto;',
                disabled: deleteDisabled,
                onclick: () => emitEvent('DeleteConnectionConfirmed'),
            }),
        ),
        () => {
            const result = getValue(props.result);
            return result
                ? Alert(
                    { type: result.success ? 'success' : 'error', class: 'mt-3' },
                    div(result.message),
                )
                : '';
        },
    );
};

const stylesheet = new CSSStyleSheet();
stylesheet.replace(`
`);

export { ConnectionDeleteConfirmation };
