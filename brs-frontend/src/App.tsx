import "./App.css";
import { Snackbar } from "@mui/joy";
import axios from "axios";
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
      {errs.map((err) => (
        <Snackbar
          key={err.message}
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
