import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import {
  Card,
  Box,
  LinearProgress,
  CardHeader,
  CardContent,
  TextField,
  IconButton,
  Button,
} from "@mui/material";
import axios, { AxiosError } from "axios";
import { useState } from "react";
import { useRecoilState, useSetRecoilState } from "recoil";
import { errors } from "../atoms";
import { loggedIn } from "./atoms";

export const Login = () => {
  const [isLoggedIn, setIsLoggedIn] = useRecoilState(loggedIn);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [password, _setPassword] = useState(
    localStorage.getItem("brs-password") ?? ""
  );
  const [passwordVisible, setPasswordVisibility] = useState(false);
  const setErrors = useSetRecoilState(errors);
  const setPassword = (password: string) => {
    localStorage.setItem("brs-password", password);
    _setPassword(password);
  };
  const handleLogin = () => {
    if (!password) {
      return;
    }
    setIsLoggingIn(true);
    axios
      .get("/api/login/", { params: { password } })
      .then(() => {
        setIsLoggedIn(true);
      })
      .catch((err) => {
        setErrors((errors) => [...errors, new AxiosError("Login failed")]);
      })
      .finally(() => {
        setIsLoggingIn(false);
      });
  };

  const setIconVisiblity = () => {
    setPasswordVisibility(!passwordVisible);
  };

  return (
    <Card
      sx={{
        maxWidth: "500px",
        width: "95%",
        overflow: "visible",
        my: 2,
        opacity: isLoggedIn ? 0.5 : 1,
      }}
    >
      <Box height={4}>{isLoggingIn && <LinearProgress />}</Box>
      <CardHeader title="BRS password" />
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleLogin();
        }}
      ></form>
      <CardContent>
        <Box p={2}>
          <TextField
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type={passwordVisible ? "text" : "password"}
            InputProps={{
              endAdornment: (
                <IconButton onClick={setIconVisiblity}>
                  {passwordVisible ? <Visibility /> : <VisibilityOff />}
                </IconButton>
              ),
            }}
          />
        </Box>
        <Box p={2} display="flex" justifyContent="flex-end">
          <Button
            variant="contained"
            onClick={handleLogin}
            disabled={password === "" || isLoggingIn || isLoggedIn}
          >
            Login
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};
