const { spawn } = require('child_process');

function runScript(command, args, name) {
    const process = spawn(command, args, { stdio: 'inherit', shell: true });
    process.on('close', (code) => {
        console.log(`[${name}] process exited with code ${code}`);
    });
    return process;
}

console.log('🔥 GigaChad Dev Server is starting...');
console.log('Starting backend server...');

const backend = runScript('./venv/bin/python', ['run_server.py'], 'BACKEND');

function cleanup() {
    console.log('Shutting down server...');
    backend.kill();
}

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup); 