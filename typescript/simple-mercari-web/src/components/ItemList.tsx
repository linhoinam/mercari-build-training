import { useEffect, useState } from 'react';
import { Item, fetchItems } from '~/api';

interface Prop {
  reload: boolean;
  setReload: (value: boolean) => void;
}

export const ItemList = ({ reload, setReload }: Prop) => {
  const [items, setItems] = useState<Item[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchItems();
        console.debug('GET success:', data);
        setItems(data.items);
      } catch (error) {
        console.error('GET error:', error);
      } finally {
        setReload(false);
      }
    };

    if (reload) {
      fetchData();
    }
  }, [reload, setReload]);

  return (
    <div className="ItemList">
      {items?.map((item) => (
        <div key={item.id} className="Item">
          <img
            src={item.image_name ? `http://localhost:9000/image/${item.image_name}` : '/logo192.png'}
            alt={item.name}
          />
          <p>
            <strong>{item.name}</strong>
            <br />
            <span>Category: {item.category}</span>
          </p>
        </div>
      ))}
    </div>
  );
};