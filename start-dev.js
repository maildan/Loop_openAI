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

// 개발 모드 환경 변수 설정 (NODE_ENV)
const env = { ...process.env, NODE_ENV: 'development' };

const backend = spawn('./venv/bin/python', ['run_server.py'], {
    stdio: 'inherit',
    shell: true,
    env,
});

backend.on('close', (code) => {
    console.log(`[BACKEND] process exited with code ${code}`);
});

function runCleanup() {
    console.log('Shutting down server...');
    backend.kill();
}

process.on('SIGINT', runCleanup);
process.on('SIGTERM', runCleanup); 