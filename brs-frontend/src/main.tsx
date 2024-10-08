import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { RecoilRoot } from "recoil";
import App from "./App";
import { Brs } from "./brs/App";
import { MasterScoreboard } from "./masterscoreboard/App";

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
const theme = createTheme({
  spacing: 4,
});

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <RecoilRoot>
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <CssBaseline />
      <ThemeProvider theme={theme}>
        <RouterProvider router={router} />
      </ThemeProvider>
    </LocalizationProvider>
  </RecoilRoot>
);
