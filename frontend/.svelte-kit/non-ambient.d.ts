
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	type MatcherParam<M> = M extends (param : string) => param is (infer U extends string) ? U : string;

	export interface AppTypes {
		RouteId(): "/" | "/albums" | "/albums/[id]" | "/albums/[albumId]" | "/login" | "/photos" | "/photos/[photoId]" | "/photos/[id]" | "/register" | "/timeline" | "/timeline/[username]" | "/users" | "/users/[username]";
		RouteParams(): {
			"/albums/[id]": { id: string };
			"/albums/[albumId]": { albumId: string };
			"/photos/[photoId]": { photoId: string };
			"/photos/[id]": { id: string };
			"/timeline/[username]": { username: string };
			"/users/[username]": { username: string }
		};
		LayoutParams(): {
			"/": { id?: string; albumId?: string; photoId?: string; username?: string };
			"/albums": { id?: string; albumId?: string };
			"/albums/[id]": { id: string };
			"/albums/[albumId]": { albumId: string };
			"/login": Record<string, never>;
			"/photos": { photoId?: string; id?: string };
			"/photos/[photoId]": { photoId: string };
			"/photos/[id]": { id: string };
			"/register": Record<string, never>;
			"/timeline": { username?: string };
			"/timeline/[username]": { username: string };
			"/users": { username?: string };
			"/users/[username]": { username: string }
		};
		Pathname(): "/" | "/albums" | `/albums/${string}` & {} | "/login" | `/photos/${string}` & {} | "/register" | "/timeline" | `/timeline/${string}` & {} | `/users/${string}` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): string & {};
	}
}