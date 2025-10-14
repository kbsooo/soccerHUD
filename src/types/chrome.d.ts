interface ChromeRuntime {
  onInstalled: {
    addListener(callback: () => void): void;
  };
  getURL(path: string): string;
}

declare const chrome: {
  runtime: ChromeRuntime;
};
