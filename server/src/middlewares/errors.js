const Boom = require("boom");
const config = require("../config");

module.exports = async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    if (!Boom.isBoom(err)) {
      Boom.boomify(err);
    }

    ctx.status = err.output.statusCode;
    ctx.body = err.output.payload;
    ctx.app.emit("error", err, ctx);
  }
};
