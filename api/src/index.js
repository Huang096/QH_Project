import express from 'express';
import router from 'endpoints/index';
import compression from 'compression';

const app = express();

app.use(compression());
app.use('/api/v2', router);

app.listen(8081);
