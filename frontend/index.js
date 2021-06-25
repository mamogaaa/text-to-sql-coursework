const StaticServer = require('static-server');

const server = new StaticServer({
  rootPath: 'public',
  port: process.env.PORT || 3005,
  host: '0.0.0.0',
  cors: '*',
});
 
server.start(function () {
  console.log('Server listening to', server.port);
});