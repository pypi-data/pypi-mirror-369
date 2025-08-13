import { ConnectionList } from './pages/connection_list.js';
import { ConnectionWizard } from './pages/connection_wizard.js';
import { EditConnection } from './pages/edit_connection.js';
import { ConnectionDeleteConfirmation } from './pages/delete_confirmation.js';

const components = {
    connections: ConnectionList,
    edit_connection: EditConnection,
    connection_wizard: ConnectionWizard,
    connection_delete_confirmation: ConnectionDeleteConfirmation,
};

export { components };
