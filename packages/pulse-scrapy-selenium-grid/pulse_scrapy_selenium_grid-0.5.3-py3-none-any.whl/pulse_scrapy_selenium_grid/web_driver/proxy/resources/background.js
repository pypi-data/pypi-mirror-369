var proxyConfig = {
  mode: "fixed_servers",
  rules: {
    singleProxy: {
      scheme: "http",
      host: "${PROXY_HOST}",
      port: parseInt("${PROXY_PORT}")
    },
    bypassList: ["localhost"]
  }
};

chrome.proxy.settings.set({value: proxyConfig, scope: "regular"}, function () {});

function callbackFn(details) {
  return {
    authCredentials: {
      username: "${PROXY_USERNAME}",
      password: "${PROXY_PASSWORD}"
    }
  };
}

chrome.webRequest.onAuthRequired.addListener(
  callbackFn,
  {urls: ["<all_urls>"]},
  ['blocking']
);
