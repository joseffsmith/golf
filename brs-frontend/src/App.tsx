import { Snackbar } from "@mui/joy";
import axios from "axios";
import { Outlet } from "react-router-dom";
import { useRecoilState } from "recoil";
import "./App.css";
import { errors } from "./atoms";
import Layout from "./Layout";

const api_key = import.meta.env.VITE_API_SECRET;
if (!api_key) {
  throw new Error("API key not found");
}
axios.defaults.baseURL = window.location.origin.includes("localhost")
  ? "http://127.0.0.1:8000"
  : "/";
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
      {errs.map((err, idx) => (
        <Snackbar
          key={err.message + idx}
          open
          color="danger"
          variant="soft"
          autoHideDuration={6000}
          onClose={() => setErrors((errs) => errs.slice(1))}
        >
          Error: "{err.message}"
        </Snackbar>
      ))}
    </>
  );
};

export default App;
