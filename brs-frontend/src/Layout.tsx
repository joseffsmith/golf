import { Link, Stack } from "@mui/joy";
import { ReactNode } from "react";
import { Link as RouterLink } from "react-router-dom";

export default function Layout({ children }: { children: ReactNode }) {
  const drawer = (
    <Stack direction={"row"} gap={4} padding={2}>
      <Link variant="soft" component={RouterLink} to="/brs">
        BRS
      </Link>

      <Link variant="soft" component={RouterLink} to="/ms">
        MasterScoreboard
      </Link>
    </Stack>
  );

  return (
    <>
      {drawer}
      {children}
    </>
  );
}
