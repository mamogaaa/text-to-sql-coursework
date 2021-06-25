const Koa = require("koa");
const cors = require("@koa/cors");
const bodyParser = require("koa-bodyparser");

const config = require("./config");
const router = require("./routes");
const errorsMiddlewares = require("./middlewares/errors");

const app = new Koa();

app.use(
  cors({
    credentials: true,
  })
);

app.use(errorsMiddlewares);

app.use(
  bodyParser({
    onerror: () => {
      throw Boom.badData();
    },
  })
);

router(app);

app.listen(config.port, () => {
  console.log(`App is running on ${config.port}`);
});
