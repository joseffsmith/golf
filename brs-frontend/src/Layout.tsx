import * as React from "react";

import Box from "@mui/joy/Box";
import CssBaseline from "@mui/joy/CssBaseline";
import Divider from "@mui/joy/Divider";
import Drawer from "@mui/joy/Drawer";
import IconButton from "@mui/joy/IconButton";
import InboxIcon from "@mui/icons-material/MoveToInbox";
import List from "@mui/joy/List";
import ListItem from "@mui/joy/ListItem";
import ListItemButton from "@mui/joy/ListItemButton";
import MailIcon from "@mui/icons-material/Mail";
import MenuIcon from "@mui/icons-material/Menu";

import Typography from "@mui/joy/Typography";
import { ReactNode } from "react";
import { Link } from "react-router-dom";

const drawerWidth = 240;

interface Props {
  children: ReactNode;
  /**
   * Injected by the documentation to work in an iframe.
   * You won't need it on your project.
   */
  window?: () => Window;
}

export default function Layout(props: Props) {
  const { window } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <div>
      {/* <Toolbar /> */}
      <Divider />
      <List>
        <ListItem>
          <Link to="/brs">BRS</Link>
        </ListItem>
        <ListItem>
          <Link to="/ms">MasterScoreboard</Link>
        </ListItem>
      </List>
    </div>
  );

  const container =
    window !== undefined ? () => window().document.body : undefined;
  return <>{props.children}</>;
  // return (
  //   <Box sx={{ display: "flex", overflowY: "auto", height: "100%" }}>
  //     <AppBar
  //       position="fixed"
  //       sx={{
  //         width: { sm: `calc(100% - ${drawerWidth}px)` },
  //         ml: { sm: `${drawerWidth}px` },
  //       }}
  //     >
  //       <Toolbar>
  //         <IconButton
  //           color="inherit"
  //           aria-label="open drawer"
  //           edge="start"
  //           onClick={handleDrawerToggle}
  //           sx={{ mr: 2, display: { sm: "none" } }}
  //         >
  //           <MenuIcon />
  //         </IconButton>
  //         <Typography variant="h6" noWrap component="div">
  //           Golf booking
  //         </Typography>
  //       </Toolbar>
  //     </AppBar>
  //     <Box
  //       component="nav"
  //       sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
  //       aria-label="mailbox folders"
  //     >
  //       {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
  //       <Drawer
  //         container={container}
  //         variant="temporary"
  //         open={mobileOpen}
  //         onClose={handleDrawerToggle}
  //         ModalProps={{
  //           keepMounted: true, // Better open performance on mobile.
  //         }}
  //         sx={{
  //           display: { xs: "block", sm: "none" },
  //           "& .MuiDrawer-paper": {
  //             boxSizing: "border-box",
  //             width: drawerWidth,
  //           },
  //         }}
  //       >
  //         {drawer}
  //       </Drawer>
  //       <Drawer
  //         variant="permanent"
  //         sx={{
  //           display: { xs: "none", sm: "block" },
  //           "& .MuiDrawer-paper": {
  //             boxSizing: "border-box",
  //             width: drawerWidth,
  //           },
  //         }}
  //         open
  //       >
  //         {drawer}
  //       </Drawer>
  //     </Box>
  //     <Box
  //       component="main"
  //       sx={{
  //         flexGrow: 1,

  //         // width: { sm: `calc(100% - ${drawerWidth}px)` },
  //         display: "flex",
  //         flexDirection: "column",
  //         alignItems: "center",
  //         justifyContent: "flex-start",
  //         height: "100%",
  //         width: "100%",
  //       }}
  //     >
  //       <Toolbar />
  //       {props.children}
  //     </Box>
  //   </Box>
  // );
}
