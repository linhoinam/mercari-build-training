import { useState, useEffect } from 'react';
import './App.css';
import { ItemList } from '~/components/ItemList';
import { Listing } from '~/components/Listing';

function App() {
  const [reload, setReload] = useState(true);

  useEffect(() => {
    setReload(true);
  }, []);

  return (
    <div>
      <header className="Title">
        <p>
          <b>Simple Mercari</b>
        </p>
      </header>
      <div>
        <Listing setReload={setReload} />
      </div>
      <div>
        <ItemList reload={reload} setReload={setReload} />
      </div>
    </div>
  );
}

export default App;