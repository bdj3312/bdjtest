// import express from 'express';
// import { readFile } from 'fs/promises';
// import net from 'net';
// import cors from 'cors';
// import bodyParser from 'body-parser';


const express = require('express');
const { readFile } = require('fs/promises');
const net = require('net');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.options('*', cors());

// 포트 번호 읽기
const readPort = async () => {
    try {
        const data = await readFile('C:\\Temp\\KAKAUTO\\port.txt', 'utf8');
        return data.trim();
    } catch (err) {
        throw err;
    }
};


app.post('/sendMessage', async (req, res) => {
    try {
        // const port = await readPort();
        const port = 40000
        console.log(port)
        const SERVER_HOST = '127.0.0.1';
        const 친구닉네임 = req.body.params[0]; // 친구 닉네임 배열
        const 카톡메세지내용 = req.body.params[2]; // 카톡 메시지 내용
        
        // 친구 닉네임 배열을 순회하여 각각의 친구에게 메시지 전송
        친구닉네임.forEach(async (친구이름) => {
            const client = new net.Socket();

            client.connect(port, SERVER_HOST, () => {
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
        console.error('포트 번호를 읽는 동안 오류 발생:', err);
        res.status(500).send('Error occurred while reading port');
    }
});

app.listen(4848, () => {
    console.log('Server running on port ');
});