
import root from '../root.svelte';
import { set_building, set_prerendering } from '__sveltekit/environment';
import { set_assets } from '$app/paths/internal/server';
import { set_manifest, set_read_implementation } from '__sveltekit/server';
import { set_private_env, set_public_env } from '../../../node_modules/@sveltejs/kit/src/runtime/shared-server.js';

export const options = {
	app_template_contains_nonce: false,
	async: false,
	csp: {"mode":"auto","directives":{"upgrade-insecure-requests":false,"block-all-mixed-content":false},"reportOnly":{"upgrade-insecure-requests":false,"block-all-mixed-content":false}},
	csrf_check_origin: false,
	csrf_trusted_origins: [],
	embedded: false,
	env_public_prefix: 'PUBLIC_',
	env_private_prefix: '',
	hash_routing: false,
	hooks: null, // added lazily, via `get_hooks`
	preload_strategy: "modulepreload",
	root,
	service_worker: false,
	service_worker_options: undefined,
	server_error_boundaries: false,
	templates: {
		app: ({ head, body, assets, nonce, env }) => "<!doctype html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"utf-8\" />\n    <link rel=\"icon\" href=\"" + assets + "/favicon.png\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n    " + head + "\n    <title>Photo Gallery</title>\n    <link\n      rel=\"stylesheet\"\n      href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\"\n    />\n    <style>\n      * {\n        margin: 0;\n        padding: 0;\n        box-sizing: border-box;\n      }\n\n      body {\n        font-family:\n          -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Oxygen, Ubuntu,\n          sans-serif;\n        background-color: #f5f5f5;\n        color: #333;\n      }\n\n      a {\n        color: inherit;\n        text-decoration: none;\n      }\n\n      .container {\n        max-width: 1200px;\n        margin: 0 auto;\n        padding: 0 20px;\n      }\n\n      .btn {\n        display: inline-flex;\n        align-items: center;\n        justify-content: center;\n        padding: 10px 20px;\n        border: none;\n        border-radius: 6px;\n        font-size: 14px;\n        font-weight: 500;\n        cursor: pointer;\n        transition: all 0.2s;\n      }\n\n      .btn-primary {\n        background-color: #2563eb;\n        color: white;\n      }\n\n      .btn-primary:hover {\n        background-color: #1d4ed8;\n      }\n\n      .btn-secondary {\n        background-color: #e5e7eb;\n        color: #374151;\n      }\n\n      .btn-secondary:hover {\n        background-color: #d1d5db;\n      }\n\n      .btn-danger {\n        background-color: #dc2626;\n        color: white;\n      }\n\n      .btn-danger:hover {\n        background-color: #b91c1c;\n      }\n\n      .btn-outline {\n        background-color: transparent;\n        border: 1px solid #d1d5db;\n        color: #374151;\n      }\n\n      .btn-outline:hover {\n        background-color: #f3f4f6;\n      }\n\n      .card {\n        background: white;\n        border-radius: 12px;\n        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);\n        overflow: hidden;\n      }\n\n      .form-group {\n        margin-bottom: 16px;\n      }\n\n      .form-label {\n        display: block;\n        margin-bottom: 6px;\n        font-size: 14px;\n        font-weight: 500;\n        color: #374151;\n      }\n\n      .form-input {\n        width: 100%;\n        padding: 10px 14px;\n        border: 1px solid #d1d5db;\n        border-radius: 6px;\n        font-size: 14px;\n        transition: border-color 0.2s;\n      }\n\n      .form-input:focus {\n        outline: none;\n        border-color: #2563eb;\n        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);\n      }\n\n      .form-textarea {\n        width: 100%;\n        padding: 10px 14px;\n        border: 1px solid #d1d5db;\n        border-radius: 6px;\n        font-size: 14px;\n        font-family: inherit;\n        resize: vertical;\n        min-height: 100px;\n        transition: border-color 0.2s;\n      }\n\n      .form-textarea:focus {\n        outline: none;\n        border-color: #2563eb;\n        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);\n      }\n\n      .checkbox {\n        display: flex;\n        align-items: center;\n        gap: 8px;\n        cursor: pointer;\n      }\n\n      .checkbox input {\n        width: 18px;\n        height: 18px;\n        cursor: pointer;\n      }\n\n      .error {\n        color: #dc2626;\n        font-size: 14px;\n        margin-top: 8px;\n      }\n\n      .success {\n        color: #16a34a;\n        font-size: 14px;\n        margin-top: 8px;\n      }\n    </style>\n  </head>\n  <body data-sveltekit-preload-data=\"hover\">\n    <div style=\"display: contents\">" + body + "</div>\n  </body>\n</html>\n",
		error: ({ status, message }) => "<!doctype html>\n<html lang=\"en\">\n\t<head>\n\t\t<meta charset=\"utf-8\" />\n\t\t<title>" + message + "</title>\n\n\t\t<style>\n\t\t\tbody {\n\t\t\t\t--bg: white;\n\t\t\t\t--fg: #222;\n\t\t\t\t--divider: #ccc;\n\t\t\t\tbackground: var(--bg);\n\t\t\t\tcolor: var(--fg);\n\t\t\t\tfont-family:\n\t\t\t\t\tsystem-ui,\n\t\t\t\t\t-apple-system,\n\t\t\t\t\tBlinkMacSystemFont,\n\t\t\t\t\t'Segoe UI',\n\t\t\t\t\tRoboto,\n\t\t\t\t\tOxygen,\n\t\t\t\t\tUbuntu,\n\t\t\t\t\tCantarell,\n\t\t\t\t\t'Open Sans',\n\t\t\t\t\t'Helvetica Neue',\n\t\t\t\t\tsans-serif;\n\t\t\t\tdisplay: flex;\n\t\t\t\talign-items: center;\n\t\t\t\tjustify-content: center;\n\t\t\t\theight: 100vh;\n\t\t\t\tmargin: 0;\n\t\t\t}\n\n\t\t\t.error {\n\t\t\t\tdisplay: flex;\n\t\t\t\talign-items: center;\n\t\t\t\tmax-width: 32rem;\n\t\t\t\tmargin: 0 1rem;\n\t\t\t}\n\n\t\t\t.status {\n\t\t\t\tfont-weight: 200;\n\t\t\t\tfont-size: 3rem;\n\t\t\t\tline-height: 1;\n\t\t\t\tposition: relative;\n\t\t\t\ttop: -0.05rem;\n\t\t\t}\n\n\t\t\t.message {\n\t\t\t\tborder-left: 1px solid var(--divider);\n\t\t\t\tpadding: 0 0 0 1rem;\n\t\t\t\tmargin: 0 0 0 1rem;\n\t\t\t\tmin-height: 2.5rem;\n\t\t\t\tdisplay: flex;\n\t\t\t\talign-items: center;\n\t\t\t}\n\n\t\t\t.message h1 {\n\t\t\t\tfont-weight: 400;\n\t\t\t\tfont-size: 1em;\n\t\t\t\tmargin: 0;\n\t\t\t}\n\n\t\t\t@media (prefers-color-scheme: dark) {\n\t\t\t\tbody {\n\t\t\t\t\t--bg: #222;\n\t\t\t\t\t--fg: #ddd;\n\t\t\t\t\t--divider: #666;\n\t\t\t\t}\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>\n\t\t<div class=\"error\">\n\t\t\t<span class=\"status\">" + status + "</span>\n\t\t\t<div class=\"message\">\n\t\t\t\t<h1>" + message + "</h1>\n\t\t\t</div>\n\t\t</div>\n\t</body>\n</html>\n"
	},
	version_hash: "bq27qr"
};

export async function get_hooks() {
	let handle;
	let handleFetch;
	let handleError;
	let handleValidationError;
	let init;
	

	let reroute;
	let transport;
	

	return {
		handle,
		handleFetch,
		handleError,
		handleValidationError,
		init,
		reroute,
		transport
	};
}

export { set_assets, set_building, set_manifest, set_prerendering, set_private_env, set_public_env, set_read_implementation };
