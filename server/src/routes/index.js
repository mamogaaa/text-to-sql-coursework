const Router = require("koa-router");

const router = new Router();

require("./model")(router);
require("./data")(router);

module.exports = (app) => {
  app.use(router.routes());
  app.use(router.allowedMethods());
};
