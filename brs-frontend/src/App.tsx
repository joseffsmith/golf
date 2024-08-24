import { forwardRef } from "react";

import "./App.css";
import { Snackbar } from "@mui/material";
import axios from "axios";
import MuiAlert, { AlertProps } from "@mui/material/Alert";
import { errors } from "./atoms";
import { useRecoilState } from "recoil";
import { Outlet } from "react-router-dom";
import Layout from "./Layout";

const api_key = import.meta.env.VITE_API_SECRET;
console.log(api_key);
axios.defaults.baseURL = "/";
axios.defaults.headers["X-MS-JS-API-KEY"] = api_key;
axios.defaults.headers["Content-Type"] = "application/json";

const App = () => {
  const [errs, setErrors] = useRecoilState(errors);
  axios.interceptors.response.use(
    (resp) => {
      return resp;
    },
    (err) => {
      setErrors((errors) => [...errors, err]);
      return Promise.reject(err);
    }
  );
  return (
    <>
      <Layout>
        <Outlet />
      </Layout>
      {errs.length > 0 && (
        <Snackbar
          open={!!errs.length}
          autoHideDuration={6000}
          onClose={() => setErrors((errs) => errs.slice(1))}
        >
          <Alert
            onClose={() => setErrors((errs) => errs.slice(1))}
            severity="error"
          >
            There was an issue, error: "{errs[0].message}".
          </Alert>
        </Snackbar>
      )}
    </>
  );
};

const Alert = forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export default App;
