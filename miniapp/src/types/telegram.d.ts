interface Window {
  Telegram?: {
    WebApp: {
      ready: () => void;
      expand: () => void;
      themeParams: {
        bg_color?: string;
        text_color?: string;
        hint_color?: string;
        button_color?: string;
        button_text_color?: string;
        secondary_bg_color?: string;
      };
    };
  };
}
