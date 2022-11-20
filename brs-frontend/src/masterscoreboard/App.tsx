import {
  Card,
  Box,
  LinearProgress,
  CardContent,
  Select,
  MenuItem,
  Autocomplete,
  TextField,
  FormControlLabel,
  Switch,
  CardHeader,
  Button,
} from "@mui/material";
import React, { useState } from "react";
import { useRecoilState, useRecoilValue, useRecoilValueLoadable } from "recoil";
import {
  book_comp,
  comps,
  currComp,
  loggedIn,
  passWord,
  players,
  preferredPlayers,
  sortedPlayers,
  teeTimes,
  userName,
} from "./atoms";
import { Login } from "./Login";
import { TeeTimes } from "./TeeTimes";

export const MasterScoreboard = () => {
  return (
    <main>
      <Login />
      <Comps />
    </main>
  );
};

const Comps = () => {
  const compsAtom = useRecoilValueLoadable(comps);
  const [showLadiesComps, setShowLadiesComps] = useState(false);

  const [comp, setCurrComp] = useRecoilState(currComp);

  const [partner1, setPartner1] = useState("101:~:Griffith, Rhys ");
  const [partner2, setPartner2] = useState<string | null>(null);
  const [partner3, setPartner3] = useState<string | null>(null);
  const username = useRecoilValue(userName);
  const password = useRecoilValue(passWord);
  const isLoggedIn = useRecoilValue(loggedIn);

  const tee_times = useRecoilValue(teeTimes);
  const handleSubmitJob = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!comp) {
      return;
    }
    book_comp(
      comp.id,
      [...new Set(tee_times.map((t) => `${t.hour}:${t.minute}`))],
      [partner1, partner2, partner3].filter(
        (v) => v !== null && v !== "-1:~:Select Your Name"
      ) as string[],
      username,
      password
    );
  };
  return (
    <Card
      sx={{
        width: 400,
        maxWidth: "90%",
        mx: 4,
        mb: 2,
      }}
    >
      <Box height={"4px"}>
        {compsAtom.state === "loading" && <LinearProgress />}
      </Box>
      <CardHeader title="Book comp" />
      <CardContent
        sx={{
          alignItems: "flex-start",
          flexDirection: "column",
          display: "flex",
        }}
      >
        {compsAtom.state === "hasValue" && (
          <>
            <FormControlLabel
              checked={showLadiesComps}
              onChange={() => setShowLadiesComps(!showLadiesComps)}
              control={<Switch />}
              label="Show ladies comps"
              sx={{ mb: 1 }}
            />
            <Autocomplete
              fullWidth
              value={comp}
              onChange={(e, val) => setCurrComp(val)}
              options={compsAtom.contents.filter((c) =>
                showLadiesComps ? true : c.gender !== "Ladies"
              )}
              getOptionLabel={(opt) =>
                `${formatDateTime(opt.comp_date)} - ${opt.html_description}`
              }
              renderInput={(params) => (
                <TextField {...params} label="Select comp" />
              )}
            />
            <TeeTimes />

            <Partner
              label={""}
              partner={partner1}
              setPartner={setPartner1}
              current_players={[username, partner1, partner2, partner3]}
            />
            <Partner
              label={""}
              partner={partner2}
              setPartner={setPartner2}
              current_players={[username, partner1, partner2, partner3]}
            />
            <Partner
              label={""}
              partner={partner3}
              setPartner={setPartner3}
              current_players={[username, partner1, partner2, partner3]}
            />
            <Box display="flex" width="100%" justifyContent="flex-end">
              <Button
                disabled={!isLoggedIn}
                onClick={handleSubmitJob}
                variant="contained"
              >
                Book
              </Button>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export const Partner = ({ partner, setPartner, label, current_players }) => {
  const pps = useRecoilValueLoadable(preferredPlayers);
  const sps = useRecoilValueLoadable(sortedPlayers);
  if (!(pps.state === "hasValue" && sps.state === "hasValue")) {
    return null;
  }
  const handlePartner = (an) => {
    setPartner(an === "No player" ? null : an);
  };

  return (
    <Select
      sx={{ my: 1 }}
      fullWidth
      label={label}
      value={partner === null ? "No player" : partner}
      onChange={(e) => handlePartner(e.target.value)}
      inputProps={{
        label: label,
      }}
    >
      <MenuItem value={"No player"}>No player chosen</MenuItem>
      {Object.entries(pps.contents).map(([key, val]) => {
        return (
          <MenuItem value={key} key={"pp" + key}>
            {val}
          </MenuItem>
        );
      })}
      {Object.entries(sps.contents).map(([key, val]) => {
        return (
          <MenuItem value={key} key={key}>
            {val}
          </MenuItem>
        );
      })}
    </Select>
  );
};

const formatDateTime = (time: number | null, include_time = false): string => {
  if (!time) {
    return "";
  }
  const dt = new Date(time * 1000);
  return include_time
    ? dt.toDateString() +
        " - " +
        dt.toLocaleTimeString("en-GB", {
          timeZone: "Europe/London",
          year: undefined,
        })
    : dt.toLocaleDateString("en-GB", { year: undefined });
};
