/**
 * @import { Connection, Flavor } from '../../../components/connection_form.js';
 *
 * @typedef {ConnectionWithFlavor}
 * @type {object}
 * @extends {Connection}
 * @property {Flavor} flavor
 *
 * @typedef Permissions
 * @type {object}
 * @property {boolean} is_admin
 * 
 * @typedef Properties
 * @type {object}
 * @property {string} project_code
 * @property {ConnectionWithIcon[]} connections
 * @property {Permissions} permissions
 */
import van from '../../../van.min.js';
import { Streamlit } from '../../../streamlit.js';
import { Button } from '../../../components/button.js';
import { Card } from '../../../components/card.js';
import { Caption } from '../../../components/caption.js';
import { Link } from '../../../components/link.js';
import { Alert } from '../../../components/alert.js';
import { getValue, emitEvent, loadStylesheet, resizeFrameHeightToElement, resizeFrameHeightOnDOMChange } from '../../../utils.js';
import { EMPTY_STATE_MESSAGE, EmptyState } from '../../../components/empty_state.js';
import { withTooltip } from '../../../components/tooltip.js';

const { div, h4, img, small, span } = van.tags;

/**
 * @param {Properties} props
 * @returns {HTMLElement}
 */
const ConnectionList = (props) => {
    loadStylesheet('connectionslist', stylesheet);
    Streamlit.setFrameHeight(1);
    window.testgen.isPage = true;

    const wrapperId = 'connections-list-wrapper';

    resizeFrameHeightToElement(wrapperId);
    resizeFrameHeightOnDOMChange(wrapperId);

    return div(
        { id: wrapperId, style: 'overflow-y: auto;' },
        () => {
            const projectCode = getValue(props.project_code);
            const permissions = getValue(props.permissions) ?? {is_admin: false};
            const connections = getValue(props.connections) ?? [];

            return connections.length > 0
                ? div(
                    Toolbar(permissions),
                    connections.map((connection) => Card({
                        testId: 'connection-card',
                        class: '',
                        title: div(
                            { class: 'flex-row fx-gap-2 tg-connections--card-title', 'data-testid': 'connection-card-title' },
                            withTooltip(
                                div(
                                    { style: 'position: relative; height: 21px;' },
                                    img({ src: connection.flavor.icon, width: 21, height: 21, 'data-testid': 'connection-card-title-flavor', alt: connection.flavor.flavor }),
                                ),
                                { text: connection.flavor.label, position: 'bottom-right' },
                            ),
                            h4({'data-testid': 'connection-card-title-name'}, connection.connection_name),
                        ),
                        border: true,
                        content: () => {
                            const connectionStatus = connection.status ?? {};

                            return div(
                                { class: 'flex-column fx-gap-3' },
                                div(
                                    { class: 'flex-row fx-gap-3' },
                                    div(
                                        { class: 'flex-column fx-flex fx-gap-3' },
                                        Link({
                                            label: 'View table groups',
                                            href: 'table-groups',
                                            params: { 'project_code': projectCode, 'connection_id': connection.connection_id },
                                            right_icon: 'chevron_right',
                                            right_icon_size: 20,
                                        }),
                                        div(
                                            { class: 'flex-row fx-flex fx-gap-3' },
                                            div(
                                                { class: 'flex-column fx-flex' },
                                                Caption({content: 'Host', style: 'margin-bottom: 4px;'}),
                                                span(connection.project_host || '--'),
                                            ),
                                            div(
                                                { class: 'flex-column fx-flex' },
                                                Caption({content: 'Database', style: 'margin-bottom: 4px;'}),
                                                span(connection.project_db || '--'),
                                            ),
                                            span({ class: 'fx-flex' }),
                                        ),
                                    ),
                                    permissions.is_admin
                                        ? div(
                                            { class: 'flex-column' },
                                            Button({
                                                type: 'stroked',
                                                color: 'primary',
                                                label: 'Test Connection',
                                                onclick: () => emitEvent('TestConnectionClicked', { payload: connection.connection_id }),
                                            }),
                                        )
                                        : '',
                                ),
                                Object.keys(connectionStatus).length > 0
                                    ? Alert(
                                        {type: connectionStatus.successful ? 'success' : 'error', closeable: true},
                                        div(
                                            { class: 'flex-column' },
                                            span(connectionStatus.message),
                                            connectionStatus.details ? span(connectionStatus.details) : '',
                                        )
                                    )
                                    : '',
                            )
                        },
                        actionContent: permissions.is_admin
                            ? div(
                                { class: 'flex-row fx-align-center' },
                                Button({
                                    type: 'icon',
                                    icon: 'edit',
                                    iconSize: 18,
                                    tooltip: 'Edit connection',
                                    tooltipPosition: 'left',
                                    color: 'basic',
                                    onclick: () => emitEvent('EditConnectionClicked', { payload: connection.connection_id }),
                                }),
                                Button({
                                    type: 'icon',
                                    icon: 'delete',
                                    iconSize: 18,
                                    tooltip: 'Delete connection',
                                    tooltipPosition: 'left',
                                    color: 'basic',
                                    onclick: () => emitEvent('DeleteConnectionClicked', { payload: connection.connection_id }),
                                }),
                            )
                            : undefined,
                    })),
                )
                : EmptyState({
                    icon: 'database',
                    label: 'No connections yet',
                    message: {
                        line1: EMPTY_STATE_MESSAGE.connection.line1,
                        line2: EMPTY_STATE_MESSAGE.connection.line2,
                    },
                    button: Button({
                        type: 'stroked',
                        icon: 'add',
                        label: 'Add Connection',
                        color: 'primary',
                        style: 'width: unset;',
                        disabled: !permissions.is_admin,
                        onclick: () => emitEvent('AddConnectionClicked', {}),
                    }),
                })
        },
    );
}

/**
 * 
 * @param {Permissions} permissions 
 * @returns 
 */
const Toolbar = (permissions) => {
    return div(
        { class: 'flex-row fx-align-flex-end mb-4' },
        span({ style: 'margin: 0 auto;' }),
        permissions.is_admin
            ? Button({
                type: 'stroked',
                icon: 'add',
                label: 'Add Connection',
                color: 'basic',
                style: 'background: var(--button-generic-background-color); width: unset; margin-right: 16px;',
                onclick: () => emitEvent('AddConnectionClicked', {}),
            })
            : '',
        Button({
            type: 'icon',
            icon: 'refresh',
            tooltip: 'Refresh connections list',
            tooltipPosition: 'left',
            style: 'border: var(--button-stroked-border); border-radius: 4px;',
            onclick: () => emitEvent('RefreshData', {}),
            testId: 'connections-refresh',
        }),
    );
}

const stylesheet = new CSSStyleSheet();
stylesheet.replace(`
.tg-connections--card-title h4 {
    margin: 0;
    color: var(--primary-text-color);
    font-size: 1.5rem;
    text-transform: initial;
}
`);

export { ConnectionList };
