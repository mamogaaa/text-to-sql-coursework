const Boom = require("boom");
const xmlrpc = require("xmlrpc");

const config = require("../config");

const client = xmlrpc.createClient(config.model);

const predict = (request) => {
  return new Promise((resolve, reject) => {
    client.methodCall("evaluate", [request], (err, res) => {
      if (err) {
        return reject(err);
      }
      return resolve(res);
    });
  });
};

module.exports = (router) => {
  router.post("/predict", async (ctx) => {
    if (!ctx.request.body.request) {
      throw Boom.badData("No request provided");
    }

    let res = await predict(ctx.request.body.request);
    let result = res.results;
    ctx.body = {
      success: true,
      sql: result.sql.replace("+5", "").replace("+60", "").replace("+200", ""),
      intentId: result.intent_id,
    };
  });
};
