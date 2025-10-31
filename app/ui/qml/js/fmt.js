.pragma library

var _dateFormat = "yyyy-MM-dd hh:mm:ss";

function safeText(value, fallback) {
  if (value === undefined || value === null)
    return fallback !== undefined ? fallback : "-";
  var text = String(value).trim();
  return text.length ? text : (fallback !== undefined ? fallback : "-");
}

function asNumber(value) {
  if (value === undefined || value === null || value === "")
    return undefined;
  var num = Number(value);
  return isNaN(num) ? undefined : num;
}

function formatTimestamp(value) {
  if (value === undefined || value === null || value === "")
    return "-";
  if (value instanceof Date)
    return Qt.formatDateTime(value, _dateFormat);
  if (typeof value === "number") {
    var ms = value;
    if (ms < 2000000000)
      ms = ms * 1000;
    return Qt.formatDateTime(new Date(ms), _dateFormat);
  }
  var parsed = Date.parse(value);
  if (!isNaN(parsed))
    return Qt.formatDateTime(new Date(parsed), _dateFormat);
  return safeText(value, "-");
}

function formatJson(value) {
  if (value === undefined || value === null)
    return "-";
  if (typeof value === "string") {
    var trimmed = value.trim();
    return trimmed.length ? trimmed : "-";
  }
  if (typeof value === "number" || typeof value === "boolean")
    return String(value);
  try {
    var text = JSON.stringify(value, null, 2);
    if (!text || text === "{}" || text === "[]")
      return "-";
    return text;
  } catch (err) {
    try {
      return String(value);
    } catch (error) {
      return "-";
    }
  }
}

function normalizeArray(value) {
  if (value === undefined || value === null)
    return [];
  if (Array.isArray(value))
    return value;
  if (typeof value === "string")
    return [value];
  if (typeof value === "object") {
    if (Array.isArray(value.items))
      return value.items;
    if (Array.isArray(value.list))
      return value.list;
    return [value];
  }
  return [];
}

function readValue(source, keys) {
  if (!source)
    return undefined;
  for (var i = 0; i < keys.length; ++i) {
    var key = keys[i];
    if (source[key] !== undefined)
      return source[key];
  }
  return undefined;
}

function displacementText(row) {
  if (!row)
    return "-";
  var parts = [];
  if (row.ex !== undefined)
    parts.push("X " + Number(row.ex).toFixed(3));
  if (row.ey !== undefined)
    parts.push("Y " + Number(row.ey).toFixed(3));
  if (row.ez !== undefined)
    parts.push("Z " + Number(row.ez).toFixed(3));
  return parts.length ? parts.join("  ") : "-";
}

function asFileUrl(path) {
  if (path === undefined || path === null)
    return "";
  var text = String(path);
  if (!text.length)
    return "";
  if (text.indexOf("file:") === 0)
    return text;
  var normalised = text.replace(/\\/g, "/");
  if (normalised.charAt(0) === "/")
    return "file://" + normalised;
  return "file:///" + normalised;
}

function coerceNumber(value, fallback) {
  if (value === undefined || value === null || value === "")
    return fallback;
  var num = Number(value);
  return isNaN(num) ? fallback : num;
}





