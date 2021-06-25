module.exports = {
  port: process.env.PORT || 3003,
  clickhouse: {
    url: "http://localhost",
    port: 8123,
  },
  model: {
    host: "localhost",
    port: 3004,
  },
};
