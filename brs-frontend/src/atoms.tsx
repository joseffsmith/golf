import { atom } from "recoil";

export const errors = atom<Error[]>({
  key: "errors",
  default: [],
});
