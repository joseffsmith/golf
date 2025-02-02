import {
  Autocomplete,
  AutocompleteOption,
  Box,
  Card,
  CardContent,
  ListItemContent,
  Typography,
} from "@mui/joy";
import React, { useState } from "react";
import { useRecoilState, useRecoilValue, useRecoilValueLoadable } from "recoil";
import {
  book_comp,
  Comp,
  comps,
  currComp,
  passWord,
  sortedPlayers,
  teeTimes,
  userName,
} from "./atoms";
import { Login } from "./Login";

export const MasterScoreboard = () => {
  return (
    <>
      <Box display={"flex"} width="100%" justifyContent={"flex-end"} p={2}>
        <Login />
      </Box>
      <Comps />
      {/* <Bookings /> */}
    </>
  );
};

const Comps = () => {
  const compsAtom = useRecoilValueLoadable(comps);

  const [comp, setCurrComp] = useRecoilState(currComp);

  const [partner1, setPartner1] = useState(null);
  const [partner2, setPartner2] = useState<string | null>(null);
  const [partner3, setPartner3] = useState<string | null>(null);
  const username = useRecoilValue(userName);
  const password = useRecoilValue(passWord);

  console.log(compsAtom);
  const tee_times = useRecoilValue(teeTimes);
  const handleSubmitJob = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!comp) {
      return;
    }
    book_comp(
      comp.id,
      comp["signup-date"]!,
      tee_times[0].hour,
      tee_times[0].minute,
      [partner1, partner2, partner3].filter((v) => v !== null) as string[]
    );
  };
  return (
    <Box
      maxWidth={450}
      margin={"0 auto"}
      display={"flex"}
      flexDirection={"column"}
      rowGap={2}
    >
      <Card sx={{}}>
        <Typography level="title-lg">Choose comp</Typography>
        {/* <CardHeader title="Book comp" /> */}
        <CardContent sx={{}}>
          <Autocomplete
            options={Object.values(compsAtom.contents ?? []) as Comp[]}
            value={comp}
            onChange={(e, val) => setCurrComp(val)}
            getOptionLabel={(opt) => opt.date}
            renderOption={(props, val) => (
              <AutocompleteOption key={val.date + val.name} {...props}>
                <ListItemContent>
                  <Typography level="title-md">{val.date}</Typography>
                  <Typography level="body-sm">{val.name}</Typography>
                </ListItemContent>
              </AutocompleteOption>
            )}
          />
          {compsAtom.state === "hasValue" && (
            <>
              {/* <FormControlLabel
              checked={showLadiesComps}
              onChange={() => setShowLadiesComps(!showLadiesComps)}
              control={<Switch />}
              label="Show ladies comps"
              sx={{ mb: 1 }}
            /> */}
              {/* <Autocomplete
              fullWidth
              value={comp}
              onChange={(e, val) => setCurrComp(val)}
              options={[...compsAtom.contents].sort(
                (a, b) =>
                  (a["signup-date"] ?? 100000000001) -
                  (b["signup-date"] ?? 100000000001)
              )}
              getOptionLabel={(opt) => `${opt.date} - ${opt.name}`}
              renderInput={(params) => (
                <Input {...params} label="Select comp" />
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
            </Box> */}
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export const Partner = ({ partner, setPartner, label, current_players }) => {
  // const pps = useRecoilValueLoadable(preferredPlayers);
  const sps = useRecoilValueLoadable(sortedPlayers);
  // if (!(pps.state === "hasValue" && sps.state === "hasValue")) {
  //   return null;
  // }

  const handlePartner = (an) => {
    setPartner(an === "No player" ? null : an);
  };

  if (sps.state === "loading") {
    return null;
  }
  return null;
  // <Select
  //   sx={{ my: 1 }}
  //   fullWidth
  //   label={label}
  //   value={partner === null ? "No player" : partner}
  //   onChange={(e) => handlePartner(e.target.value)}
  //   inputProps={{
  //     label: label,
  //   }}
  // >
  //   <MenuItem value={"No player"}>No player chosen</MenuItem>
  //   {/* {Object.entries(pps.contents).map(([key, val]) => {
  //     return (
  //       <MenuItem value={key} key={"pp" + key}>
  //         {val}
  //       </MenuItem>
  //     );
  //   })} */}
  //   {sps.contents.map((p) => {
  //     return (
  //       <MenuItem value={p.id} key={p.id}>
  //         {p.name}
  //       </MenuItem>
  //     );
  //   })}
  // </Select>
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
