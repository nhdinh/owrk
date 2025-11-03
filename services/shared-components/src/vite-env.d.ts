/// <reference types="vite/client" />

declare module '*.css' {
  const content: string;
  export default content;
}

declare module '*.yaml' {
  const content: string;
  export default content;
}

declare module '*.yaml?raw' {
  const content: string;
  export default content;
}

declare module 'js-yaml' {
  export function load(str: string, opts?: any): any;
  export function dump(obj: any, opts?: any): string;
}
