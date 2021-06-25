const { ClickHouse } = require("clickhouse");
const Boom = require("boom");

const config = require("../config");

const ch = new ClickHouse(config.clickhouse);

module.exports = (router) => {
  router.post("/lookup", async (ctx) => {
    if (!ctx.request.body.request) {
      throw Boom.badData("No request provided");
    }
    try {
      let req = ctx.request.body.request.replace("5000", "200");
      const res = await ch.query(req).toPromise();
      ctx.body = res;
    } catch (err) {
      throw Boom.badData(err.message);
    }
  });
};
