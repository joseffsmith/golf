import { Box, Typography, Button, Select, MenuItem } from "@mui/material";
import { useRecoilState } from "recoil";
import { teeTimes } from "./atoms";

export const TeeTimes = () => {
  const hours = ["07", "08", "09", "10", "11", "12", "13", "14", "15", "16"];
  const minutes = ["00", "10", "20", "30", "40", "50"];

  const [tts, setTeeTimes] = useRecoilState(teeTimes);

  const handleAddTeeTime = () => {
    setTeeTimes([
      ...tts,
      { hour: "08", minute: "30", id: Math.max(...tts.map((t) => t.id)) + 1 },
    ]);
  };

  const handleRemoveTeeTime = (id: number) => {
    setTeeTimes([...tts.filter((t) => t.id !== id)]);
  };
  const handleSetTeeTime = (
    id: number,
    type: "hour" | "minute",
    value: string
  ) => {
    const ts = [
      ...tts.map((t) => {
        if (t.id !== id) {
          return t;
        }
        return {
          ...t,
          [type]: value,
        };
      }),
    ];
  };
  return (
    <Box display="flex" textAlign={"left"} flexDirection="column" py={2}>
      <Typography>Tee time:</Typography>
      <Typography variant="subtitle2">
        All of these slots may not be available on the day, set more than one,
        order matters
      </Typography>
      <Button onClick={handleAddTeeTime}>Add tee time</Button>
      {tts.map((t) => {
        return (
          <Box key={t.id} display="flex">
            <Select<string>
              size="small"
              value={t.hour}
              onChange={(e) => handleSetTeeTime(t.id, "hour", e.target.value)}
            >
              {hours.map((h) => {
                return (
                  <MenuItem key={h} value={h}>
                    {h}
                  </MenuItem>
                );
              })}
            </Select>
            <Select<string>
              size="small"
              value={t.minute}
              onChange={(e) => handleSetTeeTime(t.id, "minute", e.target.value)}
            >
              {minutes.map((h) => {
                return (
                  <MenuItem key={h} value={h}>
                    {h}
                  </MenuItem>
                );
              })}
            </Select>
            <Button onClick={() => handleRemoveTeeTime(t.id)}>Remove</Button>
          </Box>
        );
      })}
    </Box>
  );
};
