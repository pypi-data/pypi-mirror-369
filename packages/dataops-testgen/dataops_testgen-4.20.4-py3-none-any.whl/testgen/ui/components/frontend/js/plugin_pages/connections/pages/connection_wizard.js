/**
 * @import { ConnectionStatus, Flavor } from '../../../components/connection_form.js';
 * @import { TableGroupPreview } from '../../../components/table_group_test.js';
 * 
 * @typedef WizardResult
 * @type {object}
 * @property {boolean} success
 * @property {string} message
 * @property {string} connection_id
 * @property {string} table_group_id
 *
 * @typedef Properties
 * @type {object}
 * @property {string} project_code
 * @property {Array.<Flavor>} flavors
 * @property {ConnectionStatus?} connection_status
 * @property {TableGroupPreview?} table_group_preview
 * @property {WizardResult} results
 */

import van from '../../../van.min.js';
import { Streamlit } from '../../../streamlit.js';
import { emitEvent, getValue, resizeFrameHeightOnDOMChange, resizeFrameHeightToElement } from '../../../utils.js';
import { DatabaseFlavorSelector } from './flavor_selector.js';
import { Button } from '../../../components/button.js';
import { TableGroupForm } from '../../../components/table_group_form.js';
import { TableGroupTest } from '../../../components/table_group_test.js';
import { ConnectionForm } from '../../../components/connection_form.js';
import { Checkbox } from '../../../components/checkbox.js';
import { Icon } from '../../../components/icon.js';
import { Alert } from '../../../components/alert.js';
import { Caption } from '../../../components/caption.js';

const { div, i, span, strong } = van.tags;
const stepsTitle = {
    flavor: 'Select database type',
    connection: 'Fill in the connection details',
    tableGroup: 'Create a Table Group',
    testTableGroup: 'Preview Table Group',
    runProfiling: 'Run Profiling',
};

/**
 * @param {Properties} props
 */
const ConnectionWizard = (props) => {
    Streamlit.setFrameHeight(1);
    window.testgen.isPage = true;

    const steps = [
        'flavor',
        'connection',
        'tableGroup',
        'testTableGroup',
        'runProfiling',
    ];
    const stepsState = {
        flavor: van.state(null),
        connection: van.state({ project_code: getValue(props.project_code) }),
        tableGroup: van.state({}),
        testTableGroup: van.state(false),
        runProfiling: van.state(true),
    };
    const stepsValidity = {
        flavor: van.state(false),
        connection: van.state(false),
        tableGroup: van.state(false),
        testTableGroup: van.state(false),
        runProfiling: van.state(true),
    };
    const cache = {
        privateKeyFile: null,
    };
    const currentStepIndex = van.state(0);
    const currentStepIsInvalid = van.derive(() => {
        const stepKey = steps[currentStepIndex.val];
        return !stepsValidity[stepKey].val;
    });
    const nextButtonType = van.derive(() => {
        const isLastStep = currentStepIndex.val === steps.length - 1;
        return isLastStep ? 'flat' : 'stroked';
    });
    const nextButtonLabel = van.derive(() => {
        const isLastStep = currentStepIndex.val === steps.length - 1;
        if (isLastStep) {
            return stepsState.runProfiling.val ? 'Save & Run Profiling' : 'Finish Setup';
        }
        return 'Next';
    });

    van.derive(() => {
        const tableGroupPreview = getValue(props.table_group_preview);
        stepsValidity.testTableGroup.val = tableGroupPreview?.success ?? false;
        stepsState.testTableGroup.val = tableGroupPreview?.success ?? false;
    });

    const saveConnection = () => {
        const payload = {
            connection: stepsState.connection.val,
            table_group: stepsState.tableGroup.val,
            table_group_verified: stepsState.testTableGroup.val,
            run_profiling: stepsState.runProfiling.val,
        };
        emitEvent('SaveConnectionClicked', { payload });
    };

    const setStep = (stepIdx) => {
        currentStepIndex.val = stepIdx;
    };
    const domId = 'connections-wizard-wrapper';

    resizeFrameHeightToElement(domId);
    resizeFrameHeightOnDOMChange(domId);

    return div(
        { id: domId, class: 'tg-connection-wizard flex-column fx-gap-3' },
        div(
            {},
            () => {
                const stepName = steps[currentStepIndex.val];
                const stepNumber = currentStepIndex.val + 1;
                return Caption({
                    content: `Step ${stepNumber} of ${steps.length}: ${stepsTitle[stepName]}`,
                });
            },
        ),
        WizardStep(0, currentStepIndex, () => {
            currentStepIndex.val;

            return DatabaseFlavorSelector({
                flavors: props.flavors,
                selected: stepsState.flavor.rawVal,
                onChange: (idx, flavor) => {
                    if (stepsState.flavor.val !== idx) {
                        stepsState.connection.val = {
                            ...stepsState.connection.rawVal,
                            project_port: undefined,
                            url: flavor.connection_string,
                        };
                    }

                    stepsState.flavor.val = idx;
                    stepsValidity.flavor.val = true;
                },
            });
        }),
        WizardStep(1, currentStepIndex, () => {
            currentStepIndex.val;
            const connectionStatus = props.connection_status.val;

            const flavors = props.flavors?.rawVal ?? [];
            const selectedFlavorIdx = stepsState.flavor.rawVal;
            const selectedFlavor = flavors.find((_, idx) => idx === selectedFlavorIdx);

            if (!selectedFlavor) {
                return '';
            }

            return ConnectionForm({
                connection: {
                    ...stepsState.connection.rawVal,
                    sql_flavor: selectedFlavor.flavor,
                    sql_flavor_code: selectedFlavor.value,
                    status: connectionStatus,
                },
                flavors: [ selectedFlavor ],
                disableFlavor: true,
                cachedPrivateKeyFile: cache.privateKey,
                onChange: (updatedConnection, state, formCache) => {
                    stepsState.connection.val = updatedConnection;
                    stepsValidity.connection.val = state.valid;
                    cache.privateKey = formCache.privateKey;
                },
            });
        }),
        WizardStep(2, currentStepIndex, () => {
            currentStepIndex.val;

            return TableGroupForm({
                tableGroup: stepsState.tableGroup.rawVal,
                onChange: (updatedTableGroup, state) => {
                    stepsState.tableGroup.val = updatedTableGroup;
                    stepsValidity.tableGroup.val = state.valid;
                },
            });
        }),
        WizardStep(3, currentStepIndex, () => {
            const tableGroup = stepsState.tableGroup.rawVal;

            if (currentStepIndex.val === 3) {
                const connection = stepsState.connection.rawVal;

                props.table_group_preview.val = undefined;
                stepsValidity.testTableGroup.val = false;
                stepsState.testTableGroup.val = false;

                emitEvent('PreviewTableGroupClicked', { payload: { connection, table_group: tableGroup } });
            }

            return TableGroupTest(
                tableGroup.table_group_schema ?? '--',
                props.table_group_preview,
                {
                    onVerifyAcess: () => {
                        emitEvent('PreviewTableGroupClicked', {
                            payload: {
                                connection: stepsState.connection.rawVal,
                                table_group: stepsState.tableGroup.rawVal,
                                verify_access: true,
                            },
                        });
                    }
                }
            );
        }),
        () => {
            const results = getValue(props.results);
            const runProfiling = van.state(stepsState.runProfiling.rawVal);

            van.derive(() => {
                stepsState.runProfiling.val = runProfiling.val;
            });

            return WizardStep(4, currentStepIndex, () => {
                currentStepIndex.val;

                return RunProfilingStep(
                    stepsState.tableGroup.rawVal,
                    runProfiling,
                    results,
                );
            });
        },
        div(
            { class: 'tg-connection-wizard--footer flex-row fx-justify-space-between' },
            () => currentStepIndex.val > 0 && !getValue(props.results)?.success
                ? Button({
                    label: 'Previous',
                    type: 'stroked',
                    color: 'basic',
                    width: 'auto',
                    style: 'min-width: 200px;',
                    onclick: () => setStep(currentStepIndex.val - 1),
                })
                : span(''),
            () => {
                const results = getValue(props.results);
                const runProfiling = stepsState.runProfiling.val;

                if (results && results.success && runProfiling) {
                    return Button({
                        type: 'stroked',
                        color: 'primary',
                        label: 'Go to Profiling Runs',
                        width: 'auto',
                        icon: 'chevron_right',
                        onclick: () => emitEvent('GoToProfilingRunsClicked', { payload: { table_group_id: results.table_group_id } }),
                    });
                }

                return Button({
                    label: nextButtonLabel,
                    type: nextButtonType,
                    color: 'primary',
                    width: 'auto',
                    style: 'min-width: 200px;',
                    disabled: currentStepIsInvalid,
                    onclick: () => {
                        if (currentStepIndex.val < steps.length - 1) {
                            return setStep(currentStepIndex.val + 1);
                        }

                        saveConnection();
                    },
                });
            },
        ),
    );
};

/**
 * @param {object} tableGroup
 * @param {boolean} runProfiling
 * @param {WizardResult} result
 * @returns
 */
const RunProfilingStep = (tableGroup, runProfiling, results) => {
    const disableCheckbox = van.derive(() => getValue(results)?.success ?? false);

    return div(
        { class: 'flex-column fx-gap-3' },
        Checkbox({
            label: div(
                { class: 'flex-row'},
                span({ class: 'mr-1' }, 'Execute profiling for the table group'),
                strong(() => tableGroup.table_groups_name),
                span('?'),
            ),
            checked: runProfiling,
            disabled: disableCheckbox,
            onChange: (value) => runProfiling.val = value,
        }),
        div(
            { class: 'flex-row fx-gap-1' },
            Icon({}, 'info'),
            () => runProfiling.val
                ? i('Profiling will be performed in a background process.')
                : i('Profiling will be skipped. You can run this step later from the Profiling Runs page.'),
        ),
        () => {
            const results_ = getValue(results) ?? {};
            return Object.keys(results_).length > 0
                ? Alert({ type: results_.success ? 'success' : 'error' }, span(results_.message))
                : '';
        },
    );
};

/**
 * @param {number} index
 * @param {number} currentIndex
 * @param {any} content
 */
const WizardStep = (index, currentIndex, content) => {
    const hidden = van.derive(() => getValue(currentIndex) !== getValue(index));

    return div(
        { class: () => hidden.val ? 'hidden' : ''},
        content,
    );
};

export { ConnectionWizard };
