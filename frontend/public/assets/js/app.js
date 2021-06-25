const config = {
  backendUrl: "http://localhost:3003",
};

const showError = (msg) => {
  hideResults();
  $("#error").text(`Error: ${msg}`);
  $("#error").show();
};

const hideResults = () => {
  $("#results").hide();
  $("#results-graph").hide();
};

const fillTable = (data) => {
  $("#res-table").html("");
  if (data.length == 0) {
    return;
  }

  let html = `<thead><tr>`;
  for (let title of Object.keys(data[0])) {
    html += `<th>${title}</th>`;
  }
  html += `</tr></thead>`;

  for (let row of data) {
    html += `<tr>`;
    for (let item of Object.values(row)) {
      html += `<td>${item}</td>`;
    }
    html += `</tr>`;
  }

  $("#res-table").html(html);
  $("#results").show();
};

Date.prototype.yyyymmdd = function () {
  var mm = this.getMonth() + 1;
  var dd = this.getDate();

  return [
    this.getFullYear(),
    (mm > 9 ? "" : "0") + mm,
    (dd > 9 ? "" : "0") + dd,
  ].join("-");
};

const fillGraph = (predict, data) => {
  if (predict.intentId == 1) {
    return;
  }
  $("#results-graph").show();
  Morris.Area({
    element: "graph-chart",
    data: data.map((x) => ({ y: x.timestamp.yyyymmdd(), price: x.price })),
    lineColors: ["#FF9F55"],
    xkey: "y",
    ykeys: ["price"],
    labels: ["Price"],
    pointSize: 0,
    lineWidth: 0,
    resize: true,
    fillOpacity: 0.8,
    behaveLikeLine: true,
    gridLineColor: "#5FBEAA",
    hideHover: "auto",
  });
};

const showResult = (req, predict, data) => {
  $("#req-text").text(req);
  $("#res-sql").text(predict.sql);

  let offset = 0;
  if (data.length > 0) {
    offset = new Date() - new Date(data[data.length - 1].timestamp);
  }
  data = data.map((x) => ({
    ...x,
    timestamp: new Date(new Date(x.timestamp) - -offset),
  }));
  fillTable(data);
  fillGraph(predict, data);
};

const process = async (req) => {
  $("#error").hide();
  hideResults();
  try {
    let res = await fetch(`${config.backendUrl}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ request: req }),
    });
    let predict = await res.json();
    if (parseInt(res.status / 100) != 2) {
      showError(predict.message);
      return;
    }

    res = await fetch(`${config.backendUrl}/lookup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ request: predict.sql }),
    });

    let data = await res.json();
    if (parseInt(res.status / 100) != 2) {
      showError(data.message);
      return;
    }

    showResult(req, predict, data);
  } catch (err) {
    console.log(err);
    showError(err.message);
  }
};

$(document).ready(() => {
  $("#submit").on("click", () => {
    process($("#request").val());
  });
  hideResults();
});
