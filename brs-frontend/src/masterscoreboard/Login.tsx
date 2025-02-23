import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import {
  Autocomplete,
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Input,
  LinearProgress,
  Modal,
  ModalClose,
  ModalDialog,
} from "@mui/joy";
import { InputLabel } from "@mui/material";
import axios, { AxiosError } from "axios";
import { useState } from "react";
import { useRecoilState, useSetRecoilState } from "recoil";
import { errors } from "../atoms";
import { loggedIn } from "./atoms";

export const Login = () => {
  const [changingPassword, setChangingPassword] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useRecoilState(loggedIn);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const initialPassword = localStorage.getItem("int-password") ?? "";
  const initialCourseName = localStorage.getItem("int-course") ?? null;
  const initialUsername = localStorage.getItem("int-username") ?? "";

  const [password, _setPassword] = useState(initialPassword);
  const [courseName, setCourseName] = useState<"llanishen" | "knole" | null>(
    initialCourseName as any
  );
  const [username, setUsername] = useState(initialUsername);

  const [passwordVisible, setPasswordVisibility] = useState(false);
  const setErrors = useSetRecoilState(errors);

  const handleLogin = () => {
    if (!password) {
      return;
    }

    setIsLoggingIn(true);
    axios
      .get("/api/int/login/", { params: { username, password, courseName } })
      .then(() => {
        setIsLoggedIn(true);
        localStorage.setItem("int-password", password);
        localStorage.setItem("int-course", courseName ?? "");
        localStorage.setItem("int-username", username);
        setChangingPassword(false);
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
    <>
      <Button onClick={() => setChangingPassword(true)}>Change Password</Button>
      <Modal
        open={!initialPassword || changingPassword}
        onClose={() => setChangingPassword(false)}
      >
        <ModalDialog>
          <Box height={4}>{isLoggingIn && <LinearProgress />}</Box>
          <ModalClose />
          <DialogTitle level="h4">Intelligent Golf login</DialogTitle>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleLogin();
            }}
          >
            <DialogContent>
              <InputLabel>Course Name</InputLabel>
              <Autocomplete
                value={courseName}
                onChange={(e, val) => setCourseName(val as any)}
                options={["llanishen", "knole"]}
              />
              <InputLabel>Username</InputLabel>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <InputLabel>Password</InputLabel>
              <Input
                value={password}
                onChange={(e) => _setPassword(e.target.value)}
                type={passwordVisible ? "text" : "password"}
                endDecorator={
                  <IconButton onClick={setIconVisiblity}>
                    {passwordVisible ? <Visibility /> : <VisibilityOff />}
                  </IconButton>
                }
              />
            </DialogContent>
            <DialogActions>
              <Button
                type="submit"
                disabled={password === "" || isLoggingIn || isLoggedIn}
              >
                Login
              </Button>
            </DialogActions>
          </form>
        </ModalDialog>
      </Modal>
    </>
  );
};
