import express from 'express';
import net from 'net';
import cors from 'cors';
import bodyParser from 'body-parser';

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.options('*', cors());

// Python 소켓 서버와 통신할 포트 번호
const PYTHON_SOCKET_PORT = 5000;

app.post('/sendMessage', async (req, res) => {
    try {
        const SERVER_HOST = 'localhost';
        const 친구닉네임 = req.body.params[0]; // 친구 닉네임 배열
        const 카톡메세지내용 = req.body.params[2]; // 카톡 메시지 내용
        
        // 친구 닉네임 배열을 순회하여 각각의 친구에게 메시지 전송
        친구닉네임.forEach(async (친구이름) => {
            const client = new net.Socket();

            client.connect(PYTHON_SOCKET_PORT, SERVER_HOST, () => {
                const messageObj = { "작업명": "카톡_보내기", "params": [친구이름, '채팅목록', 카톡메세지내용, 0.5] };
                const messageJson = JSON.stringify(messageObj);

                client.write(messageJson);
                console.log(`Sent to ${친구이름}: ${messageJson}`);
                client.end(); // 메시지 전송 후 소켓 연결 종료
                res.send(messageJson);
            });

            client.on('error', (err) => {
                console.error(`Error occurred while sending message to ${친구이름}:`, err.message);
                res.status(500).send(`Error occurred while sending message to ${친구이름}`);
            });
        });

    } catch (err) {
        console.error('오류 발생:', err);
        res.status(500).send('오류 발생');
    }
});

const PORT = 4848;
app.listen(PORT, () => {
    console.log(`서버가 포트 ${PORT}에서 실행 중입니다.`);
});