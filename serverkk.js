import express from 'express';
import cors from 'cors';

const port = 3000;
const app = express();
app.use(cors());

app.options('*', cors());
// GET 요청에 대한 응답
app.get('/test', (req, res) => {
    res.send('서버에서 온 응답: 요청이 성공했습니다!');
});

// 정적 파일 서빙 (client.html)
app.use(express.static('public'));

// 서버 시작
app.listen(port, () => {
    console.log(`서버가 http://localhost:${port} 에서 실행 중입니다!`);
});
