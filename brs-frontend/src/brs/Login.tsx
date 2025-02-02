import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import {
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
import axios, { AxiosError } from "axios";
import { useState } from "react";
import { useRecoilState, useSetRecoilState } from "recoil";
import { errors } from "../atoms";
import { loggedIn } from "./atoms";

export const Login = () => {
  const [changingPassword, setChangingPassword] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useRecoilState(loggedIn);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const initialPassword = localStorage.getItem("brs-password") ?? "";
  const [password, _setPassword] = useState(initialPassword);
  const [passwordVisible, setPasswordVisibility] = useState(false);
  const setErrors = useSetRecoilState(errors);

  const handleLogin = () => {
    if (!password) {
      return;
    }

    setIsLoggingIn(true);
    axios
      .get("/api/login/", { params: { password } })
      .then(() => {
        setIsLoggedIn(true);
        localStorage.setItem("brs-password", password);
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
          <DialogTitle level="h4">BRS password</DialogTitle>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleLogin();
            }}
          >
            <DialogContent>
              <Input
                // fullWidth
                value={password}
                onChange={(e) => _setPassword(e.target.value)}
                type={passwordVisible ? "text" : "password"}
                endDecorator={
                  <IconButton onClick={setIconVisiblity}>
                    {passwordVisible ? <Visibility /> : <VisibilityOff />}
                  </IconButton>
                }
              ></Input>
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
