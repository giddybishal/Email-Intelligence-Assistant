import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ChatProvider } from "./contexts/ChatContext"
import MainPage from "./pages/MainPage"

function App() {
  return(
    <BrowserRouter>
      <ChatProvider>
        <Routes>
          <Route path="/" element={<MainPage />} />
        </Routes>
      </ChatProvider>
    </BrowserRouter>
  )
}

export default App;
