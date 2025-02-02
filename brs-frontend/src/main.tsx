import { CssBaseline, ThemeProvider } from "@mui/joy";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { RecoilRoot } from "recoil";
import App from "./App";
import { Brs } from "./brs/BRS";
import { MasterScoreboard } from "./masterscoreboard/App";
import {
  experimental_extendTheme as materialExtendTheme,
  Experimental_CssVarsProvider as MaterialCssVarsProvider,
  THEME_ID as MATERIAL_THEME_ID,
} from "@mui/material/styles";
import { CssVarsProvider as JoyCssVarsProvider } from "@mui/joy/styles";

const materialTheme = materialExtendTheme();

import "./index.css";

const router = createBrowserRouter(
  [
    {
      path: "/",
      element: <App />,
      children: [
        { path: "brs", element: <Brs /> },
        { path: "ms", element: <MasterScoreboard /> },
      ],
    },
  ],
  { basename: "/golf" }
);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <RecoilRoot>
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <MaterialCssVarsProvider theme={{ [MATERIAL_THEME_ID]: materialTheme }}>
        <JoyCssVarsProvider>
          <CssBaseline enableColorScheme />
          {/* <ThemeProvider> */}
          <RouterProvider router={router} />
        </JoyCssVarsProvider>
      </MaterialCssVarsProvider>
    </LocalizationProvider>
  </RecoilRoot>
);
